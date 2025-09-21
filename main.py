from database.models import Session, Article
from scraping import crawl_sitemap, scrape, process_text
from config.logging_config import setup_log
from config import settings
from generation import run_document_agent, build_retriever
from datetime import datetime, timedelta, timezone
import time
from langchain.chat_models import init_chat_model


llm = init_chat_model('gemini-2.5-flash', model_provider="google_genai")

def run_scraper(url):
    
    with Session() as session:
        articles = crawl_sitemap(url, days=1, maxArticles=20)
        for article in articles:
            db_article = Article(title=article["title"], url=article["url"], timestamp=article["timestamp"])
            session.add(db_article) # Add a loop for for multiple articles after change
            print(f'Saved {article["title"]}')
            
        session.commit()
        
#   Check how to handle duplicate urls
        
def run():
    
    titles = []
    total_num_topics = 5
    with Session() as session:
        titles = session.query(Article.title).all()
    topics_text = llm.invoke(f"find {total_num_topics} major topics among the given titles: {titles}. Each seperated by a 'comma'. Only give topics")
    topics = topics_text.content.split(',')
    # topics = ["finance", "Athletics", "football", "basketball"]
    print(topics)
    
    retriver = build_retriever()    #   First
    
    for topic in topics:
    
        inputs = [
            f"write about {topic} based on retrieved information", 
            "write this in an intriguing mannerand mention every name, date or time exactly same as the retrived information", 
            "Save it"
        ]
        
        run_document_agent(inputs=inputs, auto=True, retriever=retriver)    #   Second
        # the following input must be given to this: 
        # {1. topic -> retrieve 2."write it in a intruiging way and mention every name, date or time exactly " -> update(optional), 3."save it"}
        time.sleep(2)
        
            
if __name__ == '__main__' :
    setup_log()
    start_urls = [
        "https://www.bbc.com/sitemaps/https-index-com-news.xml", 
        "https://www.businesstoday.in/rssfeeds/news-sitemap.xml",
        "https://www.espn.com/googlenewssitemap"    
    ]        
    #   Refer robots.txt 
    #   espncricinfo is a problem.
    
    # for start_url in start_urls:
    #     run_scraper(url=start_url)  # Add scheduling for run() and run_scraper()
    run()
    
    