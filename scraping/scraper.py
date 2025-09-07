import requests
import json
import bs4
import logging


# FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
# JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

# with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
#     data = json.load(f)

# urls = []

# # url = "https://en.wikipedia.org/w/api.php"
    
# # urls = ["https://en.wikipedia.org/wiki/Blackbeard"]

# for item in data["items"]:
#     urls.append(item["link"])



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
        logging.error(f"Error fetching {url}: {e}")
        return {} # If you take a list of urls, change to [].

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title').get_text()
    content = soup.find('div', {'class': 'mw-content-ltr'})
    paragraphs = content.find_all('p') if content else []

    results = []
    for paragraph in paragraphs:
        
        text = paragraph.get_text().strip()
        results.append(text)
    
    page_content = "\n".join(results)
    
    return {
        "title": title, 
        "content": page_content
    }

    # file_path_raw = os.path.join(
    #     FILE_PATH,
    #     "raw",
    #     f"wiki_page_{i}.txt"
    # )
    
    # with open(file_path_raw, "w", encoding="utf-8") as f:
    #     f.write(page_content)
        
    
    