import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob

ckey = 'QS0YzTmKAI2I0VLtZ7b49raaB'
csecret = 'psnulOfswOUCthCKwcQTahNtSs5hPYPI2gHUBYyplAnWQvcV32'

atoken = '17643877-WtMnPyNlhWIBIxMHSUjGxvgAODnZWwRzqxYFqRTt3'
asecret = 'WB7gWnSO8bHim3J0h1DOgdg2LYtbvC5kBthQliRxWUuFB'

#auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#auth.set_access_token(access_token, access_token_secret)

class listener(StreamListener):
    
    def on_data(self, data):
        all_data = json.loads(data)
        tweet = all_data["text"]       
        analysis = TextBlob(tweet)
        tweet.encode('utf-8', 'ignore')
        if "RT" in tweet:
            pass
        else:
            tweets=open("tweets.txt","a",encoding="utf-8")
            tweets.write(tweet)
            tweets.write('\n')
            print("\n Analysis : "+str(analysis)+"\n")
            tweets.write('\n')
#            tweets.write(str(confidence))
            tweets.write('\n\n\n')
            tweets.close()
            print(tweet, analysis)
"""            if float(analysis)*100 >= 60:
                output = open("twitter-out.txt","a")
                output.write(analysis)
                output.write('\n')
                output.close()
                return True
"""

    
    
def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=['Telugu'],languages=['en'])  
