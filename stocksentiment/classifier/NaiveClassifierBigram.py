'''
Created on May 17, 2013

@author: Sabyasachi
'''
import nltk.metrics
from nltk.collocations import BigramCollocationFinder
from nltk.tokenize.regexp import WhitespaceTokenizer
import csv
from nltk.metrics.association import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.classify.naivebayes import NaiveBayesClassifier
import collections
import utils.common
import nltk.classify.util

class NaiveClassifierBigram:
    def __init__(self):
        self.bestwords = []
        self.positivefeatures = []
        self.negativefeatures = []
        self.corpuslength = 250000
        
    def build_topn_best_words(self):
        word_fd = FreqDist()
        label_word_fd = ConditionalFreqDist()
        positivecount = 0;
        negativecount = 0
        with open(r'..\polarityData\TweetCorpus\training.1600000.processed.noemoticon.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                    #Positive sentiment tweets
                    if(row[0] == '4' and positivecount < self.corpuslength):
                        tweet = row[5]
                        tokens = WhitespaceTokenizer().tokenize(tweet)
                        #print tweet
                        for token in tokens:                        
                            word_fd.inc(token.lower())    
                            label_word_fd['pos'].inc(token.lower()) 
                        positivecount+=1
                    #Negative sentiment tweets
                    if(row[0] == '0' and negativecount < self.corpuslength):
                        tweet = row[5]
                        tokens = WhitespaceTokenizer().tokenize(tweet)
                        #print tweet
                        for token in tokens:     
                            word_fd.inc(token.lower())    
                            label_word_fd['neg'].inc(token.lower())
                        negativecount+=1
                        
        #print word_fd
        #print label_word_fd
        
        pos_word_count = label_word_fd['pos'].N()
        neg_word_count = label_word_fd['neg'].N()
        total_word_count = pos_word_count + neg_word_count
        print "Positive Word Count:", pos_word_count, "Negative Word Count:", neg_word_count, "Total Word count:", total_word_count
        
        word_scores = {}
        for word, freq in word_fd.iteritems():    
            pos_score = BigramAssocMeasures.chi_sq(label_word_fd['pos'][word], (freq, pos_word_count), total_word_count)    
            neg_score = BigramAssocMeasures.chi_sq(label_word_fd['neg'][word], (freq, neg_word_count), total_word_count)    
            word_scores[word] = pos_score + neg_score
            
        best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:10000]
        self.bestwords = set([w for w, s in best])        
        print 'Best Words Count:', len(self.bestwords)#, 'Best Words Set:', self.bestwords
            
    def evaluateclassifier(self, featureselection):
        positivecount=0
        negativecount=0
        negativetweets = []
        positivetweets = []
        #print 'Evaluating Classifier'
        print featureselection
        with open(r'..\polarityData\TweetCorpus\training.1600000.processed.noemoticon.csv', 'rb') as f:
            #print 'Opening corpus file'
            reader = csv.reader(f)
            for row in reader:
                #Positive sentiment tweets
                if(row[0] == '4' and positivecount < self.corpuslength):
                    positivetweets.append(row[5])        
                    positivecount+=1        
                #Negative sentiment tweets
                if(row[0] == '0' and negativecount < self.corpuslength):
                    negativetweets.append(row[5])
                    negativecount+=1
        
        #print 'Generating Features' 
        self.positivefeatures = [(featureselection(WhitespaceTokenizer().tokenize(tweet)), 'pos') for tweet in positivetweets]
        self.negativefeatures = [(featureselection(WhitespaceTokenizer().tokenize(tweet)), 'neg') for tweet in negativetweets]
        
        poscutoff = len(self.positivefeatures)
        negcutoff = len(self.negativefeatures)
        print "Train Pos Cutoff: " + str(poscutoff) + " Train Neg Cutoff: " + str(negcutoff)
        trainfeats = self.positivefeatures[:poscutoff] + self.negativefeatures[:negcutoff]
        
        testfeats = self.test(featureselection) 
        #testfeats = self.positivefeatures[:poscutoff] + self.negativefeatures[:negcutoff]       
        print 'Train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
        classifier = NaiveBayesClassifier.train(trainfeats)        
        print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
        
        #classifier.show_most_informative_features(20)
        
        refsets = collections.defaultdict(set)
        testsets = collections.defaultdict(set) 
        
        for i, (feats, label) in enumerate(testfeats):    
            refsets[label].add(i)    
            observed = classifier.classify(feats)  
            #print label, observed  
            testsets[observed].add(i)

        print 'pos precision:', nltk.metrics.precision(refsets['pos'], testsets['pos'])
        print 'pos recall:', nltk.metrics.recall(refsets['pos'], testsets['pos'])
        print 'pos F-measure:', nltk.metrics.f_measure(refsets['pos'], testsets['pos'])
        print 'neg precision:', nltk.metrics.precision(refsets['neg'], testsets['neg'])
        print 'neg recall:', nltk.metrics.recall(refsets['neg'], testsets['neg'])
        print 'neg F-measure:', nltk.metrics.f_measure(refsets['neg'], testsets['neg'])
        
    def test(self, featureselection):
        positiveTweets = [] 
        negativeTweets = []
        with open(r'..\polarityData\TweetCorpus\testdata.manual.2009.06.14.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                #Positive sentiment tweets
                if(row[0] == '4'):
                    positiveTweets.append(utils.common.processTweetBlank(row[5]))          
                #Negative sentiment tweets
                if(row[0] == '0'):
                    negativeTweets.append(utils.common.processTweetBlank(row[5]))
            
        positiveTestFeatures = [(featureselection(WhitespaceTokenizer().tokenize(tweet)), 'pos') for tweet in positiveTweets]
        negativeTestFeatures = [(featureselection(WhitespaceTokenizer().tokenize(tweet)), 'neg') for tweet in negativeTweets]
        
        poscutoff = len(positiveTestFeatures)
        negcutoff = len(negativeTestFeatures)
        print "Test Pos Cutoff: " + str(poscutoff) + " Test Neg Cutoff: " + str(negcutoff)
        testfeatures = positiveTestFeatures[:poscutoff] + negativeTestFeatures[:negcutoff]
        #print testfeatures
        return (testfeatures)
    
    def best_bigram_word_feats(self, words, score_fn=BigramAssocMeasures.chi_sq, n=200):    
        bigram_finder = BigramCollocationFinder.from_words(words)
        bigrams = bigram_finder.nbest(score_fn, n)
        d = dict([(bigram, True) for bigram in bigrams])
        return d

    def best_word_feats(self, words):
        return dict([(word, True) for word in words if word in self.bestwords])

    def word_feats(self, words):    
        return dict([(word, True) for word in words])
    
if __name__ == "__main__":
    corpussize = [70000]
    c = NaiveClassifierBigram()
    #c.corpuslength = 300000    
    #c.build_topn_best_words()
    #c.evaluateclassifier(c.best_word_feats)
    
    #for size in corpussize:
    #    c.corpuslength = size
    #    c.evaluateclassifier(c.word_feats)
        
    for size in corpussize:
        c.corpuslength = size
        c.evaluateclassifier(c.best_bigram_word_feats)
    