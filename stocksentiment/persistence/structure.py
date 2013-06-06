'''
Created on May 7, 2013

@author: Ashish
'''
from google.appengine.ext import ndb
import datetime

class SentimentInfo(ndb.Model):
    ticker = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    posCount = ndb.IntegerProperty()
    negCount = ndb.IntegerProperty()
    neutralCount = ndb.IntegerProperty()
    sinceId = ndb.IntegerProperty()
    watchCount = ndb.IntegerProperty()

class TweetInfo(ndb.Model):
    ticker = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    userID = ndb.StringProperty()
    userName = ndb.StringProperty()
    text = ndb.StringProperty()
    
class StockSymbol(ndb.Model):
    symbol = ndb.StringProperty()
    companyName = ndb.StringProperty()
    exchange = ndb.StringProperty()

if __name__ == '__main__':
    l = SentimentInfo()
    test = SentimentInfo(ticker='APPL', time=datetime.datetime.now(), posCount=10, negCount=2, neutralCount=50)
    test.put()
    query = SentimentInfo.query(SentimentInfo.ticker == 'APPL')
    print query.get()
