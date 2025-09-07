import requests
import os
import bs4

FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\test.txt"

urls = ["https://en.wikipedia.org/wiki/Chrysanthemum"]


for url in urls:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)


    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    content = []
    for p in soup.find_all('p'):
        content.append(p.text)
    page_content = "\n".join(content)
    page_text = soup.get_text(separator="\n", strip=True)
        
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(page_content)