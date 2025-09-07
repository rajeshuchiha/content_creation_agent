import requests
import json

API_KEY = "AIzaSyBR6g3F_r8dFBO83_0ydSU6ZZ5B35X8zv0"
SEARCH_ENGINE_ID = "7168519721da64a12"

JSON_FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data\urls.json"

query = "Chrysanthemum"

url = "https://customsearch.googleapis.com/customsearch/v1"

params = {
    'q': query,
    'key': API_KEY,
    'cx': SEARCH_ENGINE_ID,
    'num': 5
}

response = requests.get(url, params=params)
results = response.json()

with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# results = response.json()['items']

# for item in results:
#     print(item['link'])

