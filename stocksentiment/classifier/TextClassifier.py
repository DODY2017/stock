'''
Created on May 6, 2013

@author: Ashish
'''
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
import nltk.classify.util
import nltk.metrics
import nltk.tokenize as tokenize
import re
import math
import collections
import itertools
import os

class TweetClassifier(object):
    
    def __init__(self, positiveCorpus, negativeCorpus):
        self.positiveCorpus = positiveCorpus
        self.negativeCorpus = negativeCorpus

    def buildClassifier(self, feature_select):
        posFeatures = []
        negFeatures = []
        # http://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        # breaks up the sentences into lists of individual words (as selected by the input mechanism) and appends 'pos' or 'neg' after each list
        with open(self.positiveCorpus, 'r') as posSentences:
            for i in posSentences:
                posWords = re.findall(r"[\\w']+|[.,!?;]", i.rstrip())
                posWords = [feature_select(posWords), 'pos']
                posFeatures.append(posWords)
        with open(self.negativeCorpus, 'r') as negSentences:
            for i in negSentences:
                negWords = re.findall(r"[\\w']+|[.,!?;]", i.rstrip())
                negWords = [feature_select(negWords), 'neg']
                negFeatures.append(negWords)
    
        
        # selects 3/4 of the features to be used for training and 1/4 to be used for testing
        posCutoff = int(math.floor(len(posFeatures) * 3 / 4))
        negCutoff = int(math.floor(len(negFeatures) * 3 / 4))
        trainFeatures = posFeatures[:posCutoff] + negFeatures[:negCutoff]
        testFeatures = posFeatures[posCutoff:] + negFeatures[negCutoff:]
    
        # trains a Naive Bayes Classifier
        classifier = NaiveBayesClassifier.train(trainFeatures)    
    
        # initiates referenceSets and testSets
        referenceSets = collections.defaultdict(set)
        testSets = collections.defaultdict(set)    
    
        # puts correctly labeled sentences in referenceSets and the predictively labeled version in testsets
        for i, (features, label) in enumerate(testFeatures):
            referenceSets[label].add(i)
            predicted = classifier.classify(features)
            testSets[predicted].add(i)    
    
        # prints metrics to show how well the feature selection did
        print 'train on %d instances, test on %d instances' % (len(trainFeatures), len(testFeatures))
        print 'accuracy:', nltk.classify.util.accuracy(classifier, testFeatures)
        print 'pos precision:', nltk.metrics.precision(referenceSets['pos'], testSets['pos'])
        print 'pos recall:', nltk.metrics.recall(referenceSets['pos'], testSets['pos'])
        print 'neg precision:', nltk.metrics.precision(referenceSets['neg'], testSets['neg'])
        print 'neg recall:', nltk.metrics.recall(referenceSets['neg'], testSets['neg'])
        classifier.show_most_informative_features(10)
        return classifier

    
    def make_full_dict(self, words):
        return dict([(word, True) for word in words])
    
if __name__ == '__main__':
   
    tweetClassifier = TweetClassifier("C:\\work\\development\\python\\workspace\\stocksentiment\\polarityData\\rt-polaritydata\\rt-polarity-pos.txt", "C:\\work\\development\\python\\workspace\\stocksentiment\\polarityData\\rt-polaritydata\\rt-polarity-neg.txt")
    classifier = tweetClassifier.buildClassifier(tweetClassifier.make_full_dict)
    print classifier.labels()
    
