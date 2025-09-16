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

text = "T-Rex: The ultimate apex predator! 🦖💪 Unmatched size & bite force. Modern giants don't compare! #TyrannosaurusRex #DinosaurPower"
client.create_tweet(text=text)