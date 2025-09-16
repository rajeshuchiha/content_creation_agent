from database.models import Session, Article
from scraping import crawl_sitemap, scrape, process_text
from config.logging_config import setup_log
from config import settings
from generation import run_document_agent
from datetime import datetime, timedelta
import time


def run_scraper(url):
    
    with Session() as session:
        articles = crawl_sitemap(url, days=1, maxArticles=3)
        for article in articles:
            db_article = Article(title=article["title"], url=article["url"], timestamp=article["timestamp"])
            session.add(db_article) # Add a loop for for multiple articles after change
        
        session.commit()
        print(f'Saved {article["title"]}')
        
def run():
    with Session() as session:
        cutoff = datetime.now() - timedelta(days=1)
        articles = session.query(Article).filter(Article.timestamp >= cutoff).all()
        article_list = [{"id": a.id, "title": a.title, "url": a.url, "timestamp": a.timestamp.isoformat()} for a in articles]
        # with open("test_news.json", "w", encoding="utf-8") as f:
        #     json.dump(article_list, f, indent=4)
        if article_list is None:
            print(f"DataBase Outdated!. Scrape Again")
            return
            
        for article in article_list:
            page = scrape(article["url"])
            if not page.get('content'):     #   For dict -> use .get() to find the key
                return
            content = process_text(page['content'])
            print(article["url"])
            run_document_agent(text = content, auto=True)
            time.sleep(10)
        
            
if __name__ == '__main__' :
    setup_log()
    start_url = "https://www.bbc.com/sitemaps/https-index-com-news.xml"         #   Refer robots.txt of BBC
    run_scraper(url=start_url)  # Add scheduling for run() and run_scraper()
    run()