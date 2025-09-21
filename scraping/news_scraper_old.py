import requests
import json
import bs4
import logging
import time
from datetime import datetime, timedelta


# FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
# JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

# with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
#     data = json.load(f)

# site_maps = [
    #     "https://www.cnn.com/sitemaps/cnn/index.xml",
    #     "https://www.cnn.com/sitemaps/cnn/news.xml",
    #     "https://www.cnn.com/sitemap/news.xml",
    #     "https://www.cnn.com/sitemaps/sitemap-section.xml",
    #     "https://www.cnn.com/sitemaps/sitemap-interactive.xml",
    #     "https://edition.cnn.com/sitemaps/news.xml",
    #     "https://www.cnn.com/sitemap/article/cnn-underscored.xml",
    #     "https://www.cnn.com/sitemap/section/cnn-underscored.xml",
    #     "https://www.cnn.com/sitemap/section/politics.xml",
    #     "https://www.cnn.com/sitemap/article/opinions.xml",
    #     "https://www.cnn.com/sitemap/article.xml",  
    # Sitemap: https://www.cnn.com/sitemap/section.xml
    # Sitemap: https://www.cnn.com/sitemap/video.xml
    # Sitemap: https://www.cnn.com/sitemap/gallery.xml
    # Sitemap: https://www.cnn.com/sitemap/markets/stocks.xml
    # Sitemap: https://www.cnn.com/sitemap/live-story.xml
    # Sitemap: https://www.cnn.com/sitemap/election-center/politics.xml
    # Sitemap: https://www.cnn.com/sitemap/tve.xml
    # ]

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
}

def fetch(url, days=1, limit=None):

    
    try: 
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return [], [] # If you take a list of urls, change to [].

    soup = bs4.BeautifulSoup(response.content, 'xml')
    
    sitemap_urls = []
    article_urls = []
    
    if soup.find("sitemapindex"):
        sitemap_urls = [loc.get_text() for loc in soup.find_all("loc")] 
        
    elif soup.find("urlset"):
        
        for url_tag in reversed(soup.find_all("url")):
            loc = url_tag.find("loc").get_text()
            lastmod_tag = url_tag.find("lastmod")
            language = url_tag.find("news:language").get_text() # in BBC
            title = url_tag.find("news:title").get_text()
            if lastmod_tag:
                lastmod = datetime.strptime(lastmod_tag.get_text(), "%Y-%m-%dT%H:%M:%SZ")

                if(datetime.now()-lastmod < timedelta(days=days) and language =="en"):
                    article_urls.append({"title": title, "url": loc, "timestamp": lastmod})
            
        # article_urls = [loc.get_text() for loc in soup.find_all("loc")] 
        
    else:
        logging.warning(f"unknown format: {url}")
    # with open("test_news", "w", "utf-8") as f:
    #     f.write(urls[:5])
    
    # article_urls = [url for url in article_urls if not url.endswith('.jpg')]    # This was for CNN and (it was for list of urls but now it is list of dict)

    if limit is not None:
        sitemap_urls = sitemap_urls[:limit]
        article_urls = article_urls[:limit]
    
    return sitemap_urls, article_urls
        
def crawl_sitemap(start_url, days=1, maxSiteMaps=5, maxArticles=20):
    
    to_visit = [start_url]
    visited = 0
    all_articles = []
    
    while to_visit and visited < maxSiteMaps:
        current = to_visit.pop()
        logger.info(f"Processing: {current}")
        time.sleep(2)
        sitemap_urls, article_urls = fetch(current, days=days ,limit=5)
        
        if not sitemap_urls and not article_urls:
            continue
        
        visited += 1
        
        if sitemap_urls:
            to_visit.extend(sitemap_urls)
            
        if article_urls:
            all_articles.extend(article_urls)
            
        if(len(all_articles)>maxArticles): 
            break
        
    return all_articles

if __name__ == "__main__":
    start_url = "https://www.espn.com/googlenewssitemap"         #   Refer robots.txt of BBC
    articles = crawl_sitemap(start_url) 
    
    with open("test_news.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4)
    print(articles)
   
        
    
    