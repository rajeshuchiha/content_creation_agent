from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from datetime import datetime, timedelta
from database.models import Session, Article
from scraping import scrape

def build_retriever():
    # === setup vector store  ===
    
    cutoff = datetime.now() - timedelta(days=1)
    doc_list=[]
    metadata_list=[]

    with Session() as session:
        articles = session.query(Article).filter(Article.timestamp >= cutoff).all()
        article_list = [{"id": a.id, "title": a.title, "url": a.url, "timestamp": a.timestamp.isoformat()} for a in articles]
        
        if article_list is None:
            print(f"Error: DataBase OutDated")  # Maybe add "return" if later put in function.
        
        for article in article_list:
            page = scrape(article["url"])
            if not page.get('content'):     #   For dict -> use .get() to find the key
                continue
            # content = process_text(page['content'])
            content = page['content']
            meta_data = {"title": article["title"], "url": article["url"], "timestamp": article["timestamp"]}
            
            doc_list.append(content)
            metadata_list.append(meta_data)
            
            
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_split = splitter.create_documents(doc_list, metadatas=metadata_list)   # The text is split and loaded as Document list

    persist_directory = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\generation"
    collection_name = "current_news"

    #   If we don't want to define llm everytime, instead of creating vector store everytime, we can keep adding to it (guess, check if possible)
    try:
        vector_store = Chroma.from_documents(
            documents=docs_split,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=persist_directory
        )                      # Also search for chrom_cloud_api.
        print(f"Created Vector Store")
    except Exception as e:
        print(f"Error setting up Chroma DB: {str(e)}")
        raise 

    retriever = vector_store.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs = {
            "score_threshold": 0.6,
            "k": 5
        }
    )
    
     #  Also check does llm has access to metadata (and how to access it)
    #   Solution: vector_store has metadata filtering eg. vector_store.similarity_search(query, k=2, filter={"source": "twitter"}) or filter in search_kwargs
    #   Have to check how to apply this to timestamp. 
    # **Solution: For filter by datetime can use weaviate, pinecone.  