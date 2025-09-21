import requests
import json
import bs4
import logging
import time
from datetime import datetime, timedelta, timezone
from lxml import etree


# FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
# JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

# with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
#     data = json.load(f)

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

    root = etree.fromstring(response.content)
    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    }   
    #   sm is default, so not written in XML, but we have to in python
    #   Also this dictionary is compulsory.
    
    news_prefix = None
    for prefix, uri in root.nsmap.items():
        if uri == "http://www.google.com/schemas/sitemap-news/0.9":
            news_prefix = prefix if prefix else "news"
            ns[news_prefix] = uri
            break
    
    print(f"Detected namespaces: {ns}")
    print(f"News prefix: {news_prefix}")
    
    sitemap_urls = []
    article_urls = []
    
    if root.tag.endswith("sitemapindex"):

        sitemap_urls = [element.text for element in root.findall(".//sm:loc", ns)] 
        
    elif root.tag.endswith("urlset"):
        
        for url_tag in root.findall("sm:url", ns):
            
            loc = url_tag.find("sm:loc", ns).text
            language = url_tag.find(f".//{news_prefix}:language", ns).text 
            title = url_tag.find(f".//{news_prefix}:title", ns).text
            
            lastmod_tag = url_tag.find("sm:lastmod", ns)
            publication_date_tag = url_tag.find(f".//{news_prefix}:publication_date", ns)
            
            if lastmod_tag is not None:
                try:
                    lastmod = datetime.strptime(lastmod_tag.text.strip(), "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    # Handles 'Z' for UTC
                    lastmod = datetime.strptime(lastmod_tag.text.strip(), "%Y-%m-%dT%H:%M:%SZ")

                lastmod = lastmod.replace(tzinfo=timezone.utc)
                
                if(datetime.now(timezone.utc)-lastmod < timedelta(days=days) and language.strip() =="en"):
                    article_urls.append({"title": title, "url": loc, "timestamp": lastmod})
            
            elif publication_date_tag is not None:
                try:
                    pub = datetime.strptime(publication_date_tag.text.strip(), "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    # Handles 'Z' for UTC
                    pub = datetime.strptime(publication_date_tag.text.strip(), "%Y-%m-%dT%H:%M:%SZ")
                
                pub = pub.replace(tzinfo=timezone.utc)
                
                if(datetime.now(timezone.utc)-pub < timedelta(days=days) and language.strip() =="en"):
                    article_urls.append({"title": title, "url": loc, "timestamp": pub})
         
        
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
    start_url = "https://www.espncricinfo.com/sitemap.xml"         #   Refer robots.txt of BBC
    articles = crawl_sitemap(start_url) 
    
    for article in articles:
        article["timestamp"] = article["timestamp"].isoformat()
        
    with open("test_news.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4)
    print(articles)
   
        
    
    