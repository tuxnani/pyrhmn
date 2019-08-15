import tweepy
from textblob import TextBlob

consumer_key = 'QS0YzTmKAI2I0VLtZ7b49raaB'
consumer_secret = 'psnulOfswOUCthCKwcQTahNtSs5hPYPI2gHUBYyplAnWQvcV32'

access_token = '17643877-WtMnPyNlhWIBIxMHSUjGxvgAODnZWwRzqxYFqRTt3'
access_token_secret = 'WB7gWnSO8bHim3J0h1DOgdg2LYtbvC5kBthQliRxWUuFB'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.search(u'తెలుగు')
for tweet in public_tweets:
    print(tweet.text)
    analysis = TextBlob(tweet.text)
    print(analysis.sentiment)

