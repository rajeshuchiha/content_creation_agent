import requests
import bs4
import logging

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
}

def scrape(url):

    try: 
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {} # If you take a list of urls, change to [].

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    article = soup.find("article")
    if not article:
        return {}
        
    try: 
        title = article.find("h1").get_text(separator="\n", strip=True)
    except Exception as e:
        title = ""
        logger.info("Null Title due to error: {e}")
        
    try: 
        content = article.get_text(separator="\n", strip=True)
    except Exception as e:
        logger.error("Null Content due to error: {e}")
        return {}
    
       
    return {
        "title": title, 
        "content": content
    }

        
if __name__ == "__main__":
    url = "https://www.bbc.com/news/articles/c931led1q37o"
    article = scrape(url)
    with open("test_news.txt", "w", encoding="utf-8") as f:
        f.write(article["content"])
        
    print(article)