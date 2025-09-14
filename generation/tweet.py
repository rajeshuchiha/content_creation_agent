import tweepy
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.environ.get("twitter_API_key")
api_key_secret = os.environ.get("twitter_API_key_secret")
bearer_token = os.environ.get("bearer_token")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")

client = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
api = tweepy.API(auth)

text = "🏏🏆 India's glorious 2011 Cricket World Cup win at home! Dhoni's six, a nation's dream! ✨ #CWC2011 #TeamIndia #Cricket"
client.create_tweet(text=text)