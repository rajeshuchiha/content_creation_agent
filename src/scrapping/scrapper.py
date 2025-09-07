import requests
import json
import bs4
import os

FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
    
urls = []

for item in data["items"]:
    urls.append(item["link"])
    
print(urls)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
}

for i, url in enumerate(urls, start=1):
    
    response = requests.get(url, headers=headers)
    
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    
    
    page_text = soup.get_text(separator='\n', strip=True)
    
    file_path = os.path.join(
        FILE_PATH,
        f"page_{i}.txt"
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(page_text)