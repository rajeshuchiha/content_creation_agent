import requests
import json
import bs4
import os


FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

urls = []

# url = "https://en.wikipedia.org/w/api.php"
    
# urls = ["https://en.wikipedia.org/wiki/Blackbeard"]

for item in data["items"]:
    urls.append(item["link"])

params = {
    
}
    
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
}

for i, url in enumerate(urls, start=1):
    if("wikipedia" not in url): continue
    response = requests.get(url, params=params, headers=headers)

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', {'class': 'mw-content-ltr'})
    paragraphs = content.find_all('p') if content else []

    results = []
    for paragraph in paragraphs:
        
        text = paragraph.get_text().strip()
        results.append(text)

    # page_text = soup.get_text(separator='\n', strip=True)
    
    page_content = "\n".join(results)

    file_path_raw = os.path.join(
        FILE_PATH,
        "raw",
        f"wiki_page_{i}.txt"
    )
    
    with open(file_path_raw, "w", encoding="utf-8") as f:
        f.write(page_content)
        
    
    