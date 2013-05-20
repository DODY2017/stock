'''
Created on May 12, 2013

@author: Sabyasachi
'''
import csv
from nltk.tokenize import WhitespaceTokenizer
from nltk.classify.util import accuracy
from nltk.classify.api import ClassifierI
from nltk.classify.naivebayes import NaiveBayesClassifier
import nltk.metrics
import collections

class NaiveClassifierBagOfWords:
    
    def __init__(self):
        self.positiveFeatures = []
        self.negativeFeatures = []
        self.classifier = ClassifierI()
        self.local = True
    
    def word_features(self, words):
        if(isinstance(words, str)):
            return dict([(words, True)])
        if(isinstance(words, list)):
            return dict([(word, True) for word in words])
    
    def tokenize(self, line):
        tokens = WhitespaceTokenizer().tokenize(line)
        #print line, tokens   
        return(self.word_features(tokens)) 

    def parse(self):
        print 'Training file parsing in progress....'
        positiveTweets = [] 
        negativeTweets = []
        positivecount=0
        negativecount=0
        with open(r'..\polarityData\TweetCorpus\training.1600000.processed.noemoticon.csv', 'rb') as f:
            print "File Name:", f.name , "Files Open Status:", not f.closed
            reader = csv.reader(f)
            for row in reader:
                if(self.local):
                    #Positive sentiment tweets
                    if(row[0] == '4' and positivecount < 320000):
                        positiveTweets.append(row[5])          
                        positivecount+=1        
                    #Negative sentiment tweets
                    if(row[0] == '0' and negativecount < 320000):
                        negativeTweets.append(row[5])
                        negativecount+=1
                else:
                    #Positive sentiment tweets
                    if(row[0] == '4'):
                        positiveTweets.append(row[5])          
                        positivecount+=1        
                    #Negative sentiment tweets
                    if(row[0] == '0'):
                        negativeTweets.append(row[5])
                        negativecount+=1
            
        self.positiveFeatures = [(self.tokenize(f), 'pos') for f in positiveTweets]
        self.negativeFeatures = [(self.tokenize(f), 'neg') for f in negativeTweets]
            
    def train(self):
        print 'Classifier Training in progress....'
        poscutoff = len(self.positiveFeatures)
        negcutoff = len(self.negativeFeatures)
        print "Train Pos Cutoff: " + str(poscutoff) + " Train Neg Cutoff: " + str(negcutoff)
        trainfeats = self.positiveFeatures[:poscutoff] + self.negativeFeatures[:negcutoff]
        
        testfeats = self.test()        
        print 'Train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
        self.classifier = NaiveBayesClassifier.train(trainfeats)        
        print 'accuracy:', accuracy(self.classifier, testfeats)
        
        refsets = collections.defaultdict(set)
        testsets = collections.defaultdict(set) 
        
        for i, (feats, label) in enumerate(testfeats):    
            refsets[label].add(i)    
            observed = self.classifier.classify(feats)  
            #print label, observed  
            testsets[observed].add(i)

        print 'pos precision:', nltk.metrics.precision(refsets['pos'], testsets['pos'])
        print 'pos recall:', nltk.metrics.recall(refsets['pos'], testsets['pos'])
        print 'pos F-measure:', nltk.metrics.f_measure(refsets['pos'], testsets['pos'])
        print 'neg precision:', nltk.metrics.precision(refsets['neg'], testsets['neg'])
        print 'neg recall:', nltk.metrics.recall(refsets['neg'], testsets['neg'])
        print 'neg F-measure:', nltk.metrics.f_measure(refsets['neg'], testsets['neg'])
    
    def test(self):
        print 'Classifier Testing in progress....'
        positiveTweets = [] 
        negativeTweets = []
        with open(r'..\polarityData\TweetCorpus\\testdata.manual.2009.06.14.csv', 'rb') as f:
            print "File Name:", f.name , "Files Open Status:", not f.closed
            reader = csv.reader(f)
            for row in reader:
                #Positive sentiment tweets
                if(row[0] == '4'):
                    positiveTweets.append(row[5])          
                #Negative sentiment tweets
                if(row[0] == '0'):
                    negativeTweets.append(row[5])
            
        positiveTestFeatures = [(self.tokenize(f), 'pos') for f in positiveTweets]
        negativeTestFeatures = [(self.tokenize(f), 'neg') for f in negativeTweets]
        
        poscutoff = len(positiveTestFeatures)
        negcutoff = len(negativeTestFeatures)
        print "Test Pos Cutoff: " + str(poscutoff) + " Test Neg Cutoff: " + str(negcutoff)
        testfeatures = positiveTestFeatures[:poscutoff] + negativeTestFeatures[:negcutoff]
        #print testfeatures
        return (testfeatures)
    
    def classify(self, text):
        return (self.classifier.classify(self.tokenize(text)))
                
if __name__ == "__main__":
    c = NaiveClassifierBagOfWords()
    c.parse()
    c.train()
    text = 'this movie is a disaster'
    print text, 'Label:', c.classify(text)
    text = 'this movie is a great'
    print text, 'Label:', c.classify(text)