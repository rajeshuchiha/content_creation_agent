from database.models import Session, Article
from scraping.scraper import scrape
from config.logging_config import setup_log
from config import settings


def run_scraper(url):
    session = Session()
    
    article = scrape(url)
    db_article = Article(title=article["title"], url=url, content=article["content"])
    session.add(db_article) # Add a loop for for multiple articles after change
    
    session.commit()
    print(f'Saved {article["title"]}')
    
if __name__ == '__main__' :
    setup_log()
    url = "https://en.wikipia.org/wiki/Tiger"
    run_scraper(url=url)