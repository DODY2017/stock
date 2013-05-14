'''
Created on May 6, 2013

@author: Ashish
'''
from tweepy import API, Cursor, OAuthHandler, Stream
from tweepy.streaming import StreamListener
from utils import common
from persistence import structure
class Aggregator(object):
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        self.auth = auth
    def setClassfier(self, classifier):
        self.classifier = classifier
     
    def searchKeyword(self, keyword):
        api = API(self.auth)   
        for result in Cursor(api.search, q=keyword, rpp=1000).items(1000):
            try:
                  
                userID = result.from_user_id
                userName = result.from_user
                time = result.created_at
                text = result.text
                tweet = common.processTweet(text)
                print tweet
                feat = common.make_full_dict(common.getFeatureVector(tweet))
                status= self.classifier.classify(feat)
                print status
                if(status=='pos'):
                    sentimentInfo=structure.SentimentInfo(ticker=keyword,time=time,posCount=1,negCount=0)
                    sentimentInfo.put()
                else:
                    sentimentInfo=structure.SentimentInfo(ticker=keyword,time=time,posCount=0,negCount=1)
                    sentimentInfo.put()
                tweetInfo=structure.TweetInfo(ticker=keyword,time=time,userID=str(userID),userName=userName,text=text)
                tweetInfo.put()
                                                         
            except Exception, e:
                print e 
                continue 
            
    def streamReader(self, keywordList):
        feedReader = FeedListener()  
        stream = Stream(self.auth, feedReader)    
        stream.filter(follow=None, track=[keywordList])
          
          
class FeedListener(StreamListener):
    """ A listener handles tweets are the received from the stream. 
    This is a basic listener that just prints received tweets to stdout.
    """
    def setClassfier(self, classifier):
        self.classifier = classifier
         
    def on_status(self, status):
        try: 
            tweet = status.text
            print tweet
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source) 
        except Exception, e:
            print e 
            pass 
    def on_error(self, status):
        print status
        

if __name__ == '__main__':
    tweetAggregator = Aggregator("qkszpkt1i2x1kY9Ac73w", "tTNJAdzmD4tDBCbENM710TWK1UkoczHEnn8hZyO4Lwc",
                                  "996319352-9pP5LTKNyrdmLiviq47CmzasffUfZF4t0efd48", "puJC3Pv9n9QeZltBpMLYWlfD7aRLwcGuU5b29jnWkRk")
    tweetAggregator.searchKeyword('$APPL')
    tweetAggregator.streamReader('Apple')
