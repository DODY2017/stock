'''
Created on May 23, 2013

@author: Ashish
'''
from google.appengine.ext import endpoints
from protorpc import messages
from protorpc import remote

class Sentiment(messages.Message):
    category = messages.StringField(1)
    keyword= messages.StringField(2)
    
@endpoints.api(name='sentiment', version='v1', description='Sentiment API')
class SentimentAPI(remote.Service):
    @endpoints.method(request_message=Sentiment,response_message=Sentiment, name='insert', path='add', http_method='POST')
    def addSentiment(self,request):
        return request

application = endpoints.api_server([SentimentAPI])