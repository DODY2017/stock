'''
Created on May 25, 2013

@author: Sabyasachi
'''
import csv
from persistence.structure import StockSymbol

class StockSymbols:
    def store(self):
        with open(r'polarityData\stock_symbols\CompanylistNASDAQ.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'NASDAQ')
                    stock.put()
                
            query = StockSymbol.query(StockSymbol.exchange == 'NASDAQ')
            print 'NASDAQ Symbols Count:', query.count()
        
        with open(r'polarityData\stock_symbols\CompanylistAMEX.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'AMEX')
                    stock.put()
                    
            query = StockSymbol.query(StockSymbol.exchange == 'AMEX')
            print 'AMEX Symbols Count:', query.count()
        
        with open(r'polarityData\stock_symbols\CompanylistNYSE.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'NYSE')
                    stock.put()
            
            query = StockSymbol.query(StockSymbol.exchange == 'NYSE')
            print 'NYSE Symbols Count:', query.count()