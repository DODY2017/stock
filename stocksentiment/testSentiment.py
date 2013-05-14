'''
Created on May 8, 2013

@author: Ashish
'''
from classifier import TextClassifier
from tweet import aggregator
if __name__ == '__main__':
    tweetClassifier = TextClassifier.TweetClassifier("C:\\work\\development\\python\\workspace\\stocksentiment\\polarityData\\rt-polaritydata\\rt-polarity-pos.txt", "C:\\work\\development\\python\\workspace\\stocksentiment\\polarityData\\rt-polaritydata\\rt-polarity-neg.txt")
    classifier = tweetClassifier.buildClassifier(tweetClassifier.make_full_dict)
    
    tweetAggregator = aggregator.Aggregator("qkszpkt1i2x1kY9Ac73w", "tTNJAdzmD4tDBCbENM710TWK1UkoczHEnn8hZyO4Lwc",
                                  "996319352-9pP5LTKNyrdmLiviq47CmzasffUfZF4t0efd48", "puJC3Pv9n9QeZltBpMLYWlfD7aRLwcGuU5b29jnWkRk")
    tweetAggregator.setClassfier(classifier)
    tweetAggregator.searchKeyword('$APPL')
    
    print classifier.labels()
