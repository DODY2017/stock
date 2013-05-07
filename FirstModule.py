'''
Created on Apr 24, 2013

@author: Ashish
'''

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import re, math, collections, itertools, os
import nltk.classify.util, nltk.metrics
import nltk.tokenize as tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

consumer_key=""
consumer_secret=""
access_key = ""
access_secret = "" 
POLARITY_DATA_DIR = os.path.join('polarityData', 'rt-polaritydata')
RT_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-pos.txt')
RT_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-neg.txt')

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream. 
    This is a basic listener that just prints received tweets to stdout.
    """
    def setClassfier(self,classifier):
        self.classifier=classifier
         
    def on_status(self, status):
        try: 
            tweet=status.text
            print tweet
            tweet = processTweet(tweet)
            feat= make_full_dict(getFeatureVector(tweet))
            print classifier.classify(feat)
            #print self.classifier.classify(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source) 
        except Exception, e:
            print e 
            pass 
    def on_error(self, status):
        print status
    
    def bag_of_words(self,words):
        return dict([word, True] for word in words)
   
class KeywordTracker(object):
    def __init__(self,keyword):
        self.keyword=keyword
        self.neutral=0
        self.positive=0
        self.negative=0
        self.topNeutral= dict()
        self.topPositive= dict()
        self.topNegative= dict()
        self.totalTweets=0
    
    def addTweets(self,tweetText,polarity):
        self.totalTweets=self.totalTweets+1
        print self.totalTweets
        if(polarity>0):
            self.positive=self.positive+1
            self.topPositive[self.totalTweets]=tweetText
            print 'Positive',self.topPositive
        elif(polarity==0):
            self.neutral=self.neutral+1
            self.topNeutral[self.totalTweets]=tweetText
            print 'Neutarl',self.topNeutral
        else:
            self.negative=self.negative+1
            self.topNegative[self.totalTweets]=tweetText
            print 'Negative',self.topNegative


def processTweet(tweet):
    # process the tweets
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet

#initialize stopWords
stopWords = []
 
#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end
 
#start getStopWordList
def getStopWordList(stopWordListFileName):
    #read the stopwords file and build a list
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')
 
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end
 
#start getfeatureVector
def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector
#end


def evaluate_features(feature_select):
    posFeatures = []
    negFeatures = []
    #http://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
    #breaks up the sentences into lists of individual words (as selected by the input mechanism) and appends 'pos' or 'neg' after each list
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords = [feature_select(posWords), 'pos']
            posFeatures.append(posWords)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords = [feature_select(negWords), 'neg']
            negFeatures.append(negWords)

    
    #selects 3/4 of the features to be used for training and 1/4 to be used for testing
    posCutoff = int(math.floor(len(posFeatures)*3/4))
    negCutoff = int(math.floor(len(negFeatures)*3/4))
    trainFeatures = posFeatures[:posCutoff] + negFeatures[:negCutoff]
    testFeatures = posFeatures[posCutoff:] + negFeatures[negCutoff:]

    #trains a Naive Bayes Classifier
    classifier = NaiveBayesClassifier.train(trainFeatures)    

    #initiates referenceSets and testSets
    referenceSets = collections.defaultdict(set)
    testSets = collections.defaultdict(set)    

    #puts correctly labeled sentences in referenceSets and the predictively labeled version in testsets
    for i, (features, label) in enumerate(testFeatures):
        referenceSets[label].add(i)
        predicted = classifier.classify(features)
        testSets[predicted].add(i)    

    #prints metrics to show how well the feature selection did
    print 'train on %d instances, test on %d instances' % (len(trainFeatures), len(testFeatures))
    print 'accuracy:', nltk.classify.util.accuracy(classifier, testFeatures)
    print 'pos precision:', nltk.metrics.precision(referenceSets['pos'], testSets['pos'])
    print 'pos recall:', nltk.metrics.recall(referenceSets['pos'], testSets['pos'])
    print 'neg precision:', nltk.metrics.precision(referenceSets['neg'], testSets['neg'])
    print 'neg recall:', nltk.metrics.recall(referenceSets['neg'], testSets['neg'])
    classifier.show_most_informative_features(10)
    return classifier

#scores words based on chi-squared test to show information gain (http://streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/)
def create_word_scores():
    #creates lists of all positive and negative words
    posWords = []
    negWords = []
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords.append(posWord)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords.append(negWord)
    posWords = list(itertools.chain(*posWords))
    negWords = list(itertools.chain(*negWords))

    #build frequency distibution of all words and then frequency distributions of words within positive and negative labels
    word_fd = FreqDist()
    cond_word_fd = ConditionalFreqDist()
    for word in posWords:
        word_fd.inc(word.lower())
        cond_word_fd['pos'].inc(word.lower())
    for word in negWords:
        word_fd.inc(word.lower())
        cond_word_fd['neg'].inc(word.lower())

    #finds the number of positive and negative words, as well as the total number of words
    pos_word_count = cond_word_fd['pos'].N()
    neg_word_count = cond_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    #builds dictionary of word scores based on chi-squared test
    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score

    return word_scores

#finds word scores
word_scores = create_word_scores()

#finds the best 'number' words based on word scores
def find_best_words(word_scores, number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words

#creates feature selection mechanism that only uses best words
def best_word_features(words):
    return dict([(word, True) for word in words if word in best_words])

def make_full_dict(words):
    return dict([(word, True) for word in words])

if __name__ == '__main__':
    numbers_to_test = 15000
    best_words = find_best_words(word_scores, numbers_to_test)
    classifier = evaluate_features(best_word_features)
    print classifier.labels()
    test= "This is good"
    wordList = re.sub("[^\w]", " ",  test).split()
    print wordList
    feat= make_full_dict(wordList)
    print classifier.classify(feat)
    #print nltk.classify.util.accuracy(classifier, feat)
    
    l = StdOutListener()
    l.setClassfier(classifier)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    stream = Stream(auth, l)    
    stream.filter(follow=None,track=['$APPL'])
    
    
    # Create API Handler
    api = API(auth)
    ticker='$APPL'
    for result in Cursor(api.search,q=ticker,rpp=1000).items(1000):
        try:
            #print(dir(result)) 
            tweetUserID=result.from_user_id
            tweetUserName=result.from_user
            tweetTime =result.created_at
            #key=ticker+tweetTime+tweetUserID
            tweetTime=tweetTime.replace(second=0, microsecond=0)
            tweetText=result.text
            #print tweetText
            tweetText = processTweet(tweetText)
            print tweetTime, tweetUserName, tweetText
            feat= make_full_dict(getFeatureVector(tweetText))
            print classifier.classify(feat)                                                   
        except Exception, e:
            print e 
            continue 

   
  

