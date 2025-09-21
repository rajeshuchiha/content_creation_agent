import requests
import bs4
import logging

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
}

def scrape(url, article_title=""):

    try: 
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        logger.error(f"Error fetching {url}: {e}")
        return {} # If you take a list of urls, change to [].

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

        
    try: 
        title = soup.select_one("article h1").get_text(separator="\n", strip=True)
    except Exception as e:
        title = article_title
        logger.info("Null Title due to error: {e}")
        
    try: 
        paragraphs = soup.select("article p")
        content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
        
    except Exception as e:
        print("Null Content due to error: {e}") 
        logger.error("Null Content due to error: {e}")
        return {}
    
       
    return {
        "title": title, 
        "content": content
    }

        
if __name__ == "__main__":
    url = "https://www.cricbuzz.com/cricket-news/135648/for-kuldeep-yadav-its-all-about-making-the-overs-count"
    article = scrape(url)
    if article.get('content'):
        with open("test_news.txt", "w", encoding="utf-8") as f:
            f.write(article["content"])
            
        print(article)
    else:
        print("Null Content!")