from typing_extensions import Sequence, TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from generation.blogger import postBlog
from generation.tweet import postTweet
from database.models import Session, Article
from scraping import scrape

load_dotenv()

# AUTO_MODE = False

# def toggle_auto():
#     global AUTO_MODE    
#     AUTO_MODE = True



class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tweet: Annotated[str, "≤15 words, must include hashtags, mentions, emojis"]
    blog_post: Annotated[str, "≥250 words, detailed and informative"]
    input_index: int
       
def run_document_agent(inputs=None, auto=False, retriever=None):  
    
    if retriever is None:
        return    
    
    # # === setup vector store  ===
    
    # cutoff = datetime.now() - timedelta(days=1)
    # doc_list=[]
    # metadata_list=[]

    # with Session() as session:
    #     articles = session.query(Article).filter(Article.timestamp >= cutoff).all()
    #     article_list = [{"id": a.id, "title": a.title, "url": a.url, "timestamp": a.timestamp.isoformat()} for a in articles]
        
    #     if article_list is None:
    #         print(f"Error: DataBase OutDated")  # Maybe add "return" if later put in function.
        
    #     for article in article_list:
    #         page = scrape(article["url"])
    #         if not page.get('content'):     #   For dict -> use .get() to find the key
    #             continue
    #         # content = process_text(page['content'])
    #         content = page['content']
    #         meta_data = {"title": article["title"], "url": article["url"], "timestamp": article["timestamp"]}
            
    #         doc_list.append(content)
    #         metadata_list.append(meta_data)
            
            
    # embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # docs_split = splitter.create_documents(doc_list, metadatas=metadata_list)   # The text is split and loaded as Document list

    # persist_directory = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\generation"
    # collection_name = "current_news"

    # #   If we don't want to define llm everytime, instead of creating vector store everytime, we can keep adding to it (guess, check if possible)
    # try:
    #     vector_store = Chroma.from_documents(
    #         documents=docs_split,
    #         embedding=embeddings,
    #         collection_name=collection_name,
    #         persist_directory=persist_directory
    #     )                      # Also search for chrom_cloud_api.
    #     print(f"Created Vector Store")
    # except Exception as e:
    #     print(f"Error setting up Chroma DB: {str(e)}")
    #     raise 

    # retriever = vector_store.as_retriever(
    #     search_type = "similarity_score_threshold",
    #     search_kwargs = {
    #         "score_threshold": 0.6,
    #         "k": 5
    #     }
    # )


    #  Also check does llm has access to metadata (and how to access it)
    #   Solution: vector_store has metadata filtering eg. vector_store.similarity_search(query, k=2, filter={"source": "twitter"}) or filter in search_kwargs
    #   Have to check how to apply this to timestamp. 
    # **Solution: For filter by datetime can use weaviate, pinecone.  
        
    #------------------------------------------------------
    
       
    #   Decided not to remove update (after retrieval sent here to get the format).
    @tool 
    def update(tweet: str, blog_post: str) -> dict:
        """Updates the document with tweet and blog_post"""

        return {
            "tweet": tweet,
            "blog_post": blog_post
        }

        
    @tool
    def save(filename: str, tweet: str, blog_post: str) -> str:
        """Save the Document in a text file and finish the process.

        Args:
            filename (str): Name of the text file.
            tweet (str): A short message (max 15 words) including hashtags (#), mentions (@), w
                        and emojis 😃🔥✨ when relevant.
                        
            blog_post (str): A detailed and informative blog_post of atleast 250 words, expanding on the tweets theme.
        """
        if not filename.endswith(".txt"):
            filename = f"{filename}.txt"
            
        #post code --> write later (check the returns)
        try:
            postTweet(tweet)
            print("Tweet posted successfully!")
        except Exception as e:
            print(f"Tweet posting failed: {str(e)}")
            
        try:
            postBlog(blog_post)
            print("Blog posted successfully!")
        except Exception as e:
            print(f"Blog posting failed: {str(e)}")
                    
        #Save file code
        DATA_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
        FILE_PATH = os.path.join(DATA_PATH, filename)
        
        document_content = f"Tweet: \n{tweet}\nBlog Post: \n{blog_post}"
        try: 
            with open(FILE_PATH, "w", encoding="utf-8") as file:
                file.write(document_content)
            print(f"\n Document saved to {filename}")
            return f"Document has been saved successfully to {filename}"
        except Exception as e:
            return f"File not saved due to error: {str(e)}"
        
        
    def retriever_tool(query: str) -> str:
        """
        This tool searches and returns information from the vector store.
        """
        docs = retriever.invoke(query)
        
        if not docs:
            return f"Information not found in the retrieved docs."
        
        results = []
        
        for i, doc in enumerate(docs):
            results.append(f"Document {i+1}:\n{doc.page_content}")
            
        return "\n\n".join(results)
        
        
    tools = [retriever_tool, update, save]
    llm = init_chat_model('gemini-2.5-flash', model_provider="google_genai").bind_tools(tools)

    #   Function to automate user input
    def get_User_or_Auto_input(state: AgentState, config=None) -> HumanMessage :
        
        cfg = config.get("configurable", {}) if config else {}
        
        if cfg.get("auto_mode"):
            inputs = cfg.get("inputs")
            current_idx = state.get("input_index", 0)
            user_message = HumanMessage(content="Save it")  # Default (if not saved by previous command)
            
            if current_idx < len(inputs):
                user_input = inputs[current_idx]
                user_message = HumanMessage(content=user_input)
        
        # if AUTO_MODE:
        #     user_input = f"Save it."
        #     user_message = HumanMessage(content=user_input)
        
        elif not state["messages"]:
            user_input = "I'm ready to help you update the document. What would you like to create?"
            user_message = HumanMessage(content=user_input)
            
        else:
            user_input = input("\n How would you like to update the document?")
            print(f"\n USER: {user_input}")
            user_message = HumanMessage(content=user_input)
            
        return user_message


    def our_agent(state: AgentState, config=None) -> AgentState:
        
        system_prompt = SystemMessage(content=f"""
        You are an Intelligent AI Assistant. Your role is to retrieve information using `retriever_tool`, 
        then generate, update, or save content in strict compliance with the JSON schema below:

        {{
            "tweet": [
                "Must include hashtags (#), mentions (@), and emojis 😃🔥✨ when relevant",
                "Maximum of 15 words",
                "Concise, catchy, and engaging"
            ],
            "blog_post": [
                "At most 1000 words",
                "Detailed, informative, and engaging", 
                "Should expand on the Tweet's theme with depth and clarity",
                "Blog post must be written in valid HTML format with proper tags (<h1>, <p>, <ul>, etc.)"
            ]
        }}

        ### Rules:
        - Always call `retriever_tool` first to gather context, unless the answer is already fully in the current document.
        - **After retrieving documents**, always generate both `tweet` and `blog_post` and call the `update` tool with the full updated content
        - Always use **tools** (`update`, `save`) for any JSON output. Do NOT directly print JSON in your final reply.
        - `update` must include both the full updated "tweet" and "blog_post".
        - `save` saves both tweet and blog post content together.
        - **IMPORTANT**: After calling `save`, wait for the tool result. If you see "Document has been saved successfully", the process is complete.
        - Always generate a descriptive filename ending with `.txt` (e.g., `"tweet_marketing.txt"`, `"blog_ai_trends.txt"`).
        - Filenames must reflect the document content meaningfully.
        - Cite specific parts of retrieved information in the blog post.
        - After `update` or `save`, always pass the **entire current state** of the document as tool arguments.
        - If API posting fails but file is saved, consider it a success.

        ### Current Document:
        {{
            "tweet": "{state.get('tweet', '')}",
            "blog_post": "{state.get('blog_post', '')}"
        }}
    """)
        
        
        user_message = get_User_or_Auto_input(state, config)

        prompt = [system_prompt] + list(state["messages"]) + [user_message]
        
        response = llm.invoke(prompt)
        
        print("\nCurrent tweet:", state['tweet'])
        print("\nCurrent blog_post:", state['blog_post'])
        
        print(f"\n AI: {response.content}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"\n Using TOOLS: {[tc for tc in response.tool_calls]}")

        return {
            "messages": list(state['messages']) + [user_message, response], 
            "input_index": state["input_index"]+1, 
            "tweet": state.get("tweet", ""),
            "blog_post": state.get("blog_post", "")
        }

    def should_continue(state: AgentState):
        """Decides whether we continue or end the conversation"""
        messages = state['messages']
        
        if not messages: 
            return "continue"
        #   End if Saved
        for message in reversed(messages):
            if(isinstance(message, ToolMessage)):
            
                if ("saved successfully" in message.content.lower() or ("document has been saved" in message.content.lower())):
                    print("Found save confirmation - Ending...")  
                    return "end"
            
                if ("File not saved" in message.content.lower()):
                    print("Save Error - Ending....")
                    return "end"
                #   End if no retrieved data
            
                if ("information not found" in message.content.lower() and "retrieved docs" in message.content.lower()):
                    print("No data found - Ending.....")  
                    return "end"
        
        return "continue"

    def print_messages(messages):
        """Funtion I made to print messages in a readable format"""
        if not messages: 
            return
        
        for message in messages[-3:]:
            if isinstance(message, ToolMessage):
                print(f"\n TOOL RESULT: {message.content}")

    def create_stateful_tool_node(tools):
        
        def stateful_tool_node(state: AgentState):
            tool_node = ToolNode(tools)
            result = tool_node.invoke(state)
            
            updated_tweet = ""
            updated_blog_post = ""
        
            if state["messages"]:
                last_ai_message = state["messages"][-1]
                if hasattr(last_ai_message, "tool_calls"):
                    for tool_call in last_ai_message.tool_calls:
                        if tool_call["name"] == "update":
                            tool_args = tool_call["args"]
                            updated_tweet = tool_args["tweet"]
                            updated_blog_post = tool_args["blog_post"]
                            
            return {
                "messages": result["messages"],
                "tweet": updated_tweet,
                "blog_post": updated_blog_post
            }            
            
        return stateful_tool_node
                
    graph = StateGraph(AgentState)

    graph.add_node("tools", create_stateful_tool_node(tools))
    graph.add_node("agent", our_agent)

    graph.add_edge(START, "agent")
    graph.add_edge("agent", "tools")

    graph.add_conditional_edges(
        "tools",
        should_continue,
        {
            "continue": "agent",
            "end": END
        }
    )

    app = graph.compile()


    print("\n *****DRAFTER*****")
    
    # Toggle Automatic
    
    config = None
    
    if inputs and auto:
        config = {
            "configurable": {
                "inputs": inputs,
                "auto_mode": auto
            }
        }
        
    state = {"messages": [], 'tweet':"", 'blog_post':"", "input_index":0}

        
    for step in app.stream(state, config=config, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n***FINISHED DRAFTER***")

if __name__ == "__main__":
    run_document_agent()
            


