import os
import requests
from dotenv import load_dotenv

load_dotenv()

data = {
    "grant_type": "password",
    "username": "Ok_Turnip9330",
    "password": os.environ.get("reddit_password")
}

client_id = os.environ.get("reddit_client_ID")
client_secret = os.environ.get("reddit_client_secret")

auth = (client_id, client_secret)
headers = {"User-Agent": "test/0.1 by Ok_Turnip9330"}

response = requests.post(url="https://www.reddit.com/api/v1/access_token", data=data, auth=auth, headers=headers)


bearer_token = response.json()['access_token']
headers = {"Authorization": f"bearer {bearer_token}", "User-Agent": "ChangeMeClient/0.1 by Ok_Turnip9330"}

# response  = requests.get(url="https://oauth.reddit.com/api/v1/me", headers=headers)

# print(response.json())

# Compulsory keys for data. !!! Change "sr" to desired subreddit.
def post_reddit(sr=None, text=None):
    data = {
            "sr": "r/test",
            "kind": "self",
            "title": "First Post",
            "text": "It is fun posting this post. Easy and satisfyyying!"
    }    

    if sr is not None:
        data["sr"] = sr
        
    if text is not None:
        data["text"] = text
    
    response = requests.post(
        "https://oauth.reddit.com/api/submit", 
        data=data,
        headers=headers
    )
    print(response.json())

if __name__ == "__main__":  
# response.status_code()

    post_reddit()
