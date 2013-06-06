'''
Created on May 23, 2013

@author: Ashish
'''
from google.appengine.ext import endpoints
from protorpc import messages
from protorpc import remote
from persistence.structure import StockSymbol, SentimentInfo
from persistence.StockSymbols import StockSymbols
from google.appengine.ext import ndb
from classifier.NaiveClassifierBagOfWords import NaiveClassifierBagOfWords
from tweet.aggregator import Aggregator

class KeywordTracker(messages.Message):
    category = messages.StringField(1)
    keyword= messages.StringField(2)
    
class StockSymbolMessage(messages.Message):
    symbol = messages.StringField(1)
    companyName = messages.StringField(2)
    exchange = messages.StringField(3)
    
class StockSymbolList(messages.Message):
    items = messages.MessageField(StockSymbolMessage, 1, repeated=True)
    
class StockSymbolCountMessage(messages.Message):
    message = messages.StringField(1)
        
@endpoints.api(name='sentiment', version='v1', description='Sentiment API')
class SentimentAPI(remote.Service):
    @endpoints.method(request_message=KeywordTracker,response_message=KeywordTracker, name='addKeyword', path='add', http_method='POST')
    def addKeyword(self,request):
        sentimentInfo = SentimentInfo(category=request.category, ticker=request.keyword)        
        sentimentInfo.put()
        return request
    
    @endpoints.method(name='startSentiment', path='start', http_method='POST')
    def startSentiment(self, request):
        classifier = NaiveClassifierBagOfWords()
        tweetAggregator = Aggregator("qkszpkt1i2x1kY9Ac73w", "tTNJAdzmD4tDBCbENM710TWK1UkoczHEnn8hZyO4Lwc",
                                  "996319352-9pP5LTKNyrdmLiviq47CmzasffUfZF4t0efd48", "puJC3Pv9n9QeZltBpMLYWlfD7aRLwcGuU5b29jnWkRk")
        tweetAggregator.setClassfier(classifier)
        tweetAggregator.streamReader('Apple')
        return request

@endpoints.api(name='symbols', version='v1', description='Stock Symbols API')
class GetSymbolsAPI(remote.Service):
    @endpoints.method(response_message=StockSymbolList, name='getsymbols', path='get', http_method='GET')
    def getSymbols(self, request):
        symbols = []
        for sym in StockSymbol.query():
            symbols.append(StockSymbolMessage(symbol=sym.symbol, companyName=sym.companyName, exchange=sym.exchange))
        
        return StockSymbolList(items=symbols)
    
    @endpoints.method(name='addsymbols', path='add', http_method='POST')
    def addSymbols(self, request):
        stock = StockSymbols()
        stock.store()
        
        return request
    
    @endpoints.method(response_message=StockSymbolCountMessage, name='countsymbols', path='count', http_method='GET')
    def getSymbolCount(self, request):
        query = StockSymbol.query()
        return StockSymbolCountMessage(message=str(query.count()))
    
    @endpoints.method(response_message=StockSymbolCountMessage, name='deletesymbols', path='delete', http_method='GET')
    def deleteSymbols(self, request):
        symbolkeys = []
        for sym in StockSymbol.query():
            symbolkeys.append(sym.key)
        
        ndb.delete_multi(symbolkeys)
        message = 'All Symbols Deleted'      
        return StockSymbolCountMessage(message=message)

    
application = endpoints.api_server([SentimentAPI, GetSymbolsAPI])



