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

    article = soup.find("article")
    
    if not article:
        total_content = soup.get_text(separator="\n", strip=True)
        if not total_content:

            return {}
        return {
            "title": article_title,
            "content": total_content
        }
        
    try: 
        title = article.find("h1").get_text(separator="\n", strip=True)
    except Exception as e:
        title = article_title
        logger.info("Null Title due to error: {e}")
        
    try: 
        content = article.get_text(separator="\n", strip=True)
        print(f"{content}\n")
    except Exception as e:
        print("Null Content due to error: {e}") 
        logger.error("Null Content due to error: {e}")
        return {}
    
       
    return {
        "title": title, 
        "content": content
    }

        
if __name__ == "__main__":
    url = "https://www.espn.com/nbl/story/_/id/46301098/nbl-melbourne-united-milton-doyle-returns-ice-game-tasmania-jackjumpers"
    article = scrape(url)
    if article.get('content'):
        with open("test_news.txt", "w", encoding="utf-8") as f:
            f.write(article["content"])
            
        print(article)
    else:
        print("Null Content!")