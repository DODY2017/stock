'''
Created on May 25, 2013

@author: Sabyasachi
'''
import csv
from persistence.structure import StockSymbol
import os

class StockSymbols:
    def store(self):
        STOCK_DIR = os.path.join('polarityData', 'stock_symbols')
        NASDAQ_FILE = os.path.join(STOCK_DIR, 'CompanylistNASDAQ.csv')
        with open(NASDAQ_FILE, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'NASDAQ')
                    stock.put()
                
            query = StockSymbol.query(StockSymbol.exchange == 'NASDAQ')
            print 'NASDAQ Symbols Count:', query.count()
        
        AMEX_FILE = os.path.join(STOCK_DIR, 'CompanylistAMEX.csv')
        with open(AMEX_FILE, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'AMEX')
                    stock.put()
                    
            query = StockSymbol.query(StockSymbol.exchange == 'AMEX')
            print 'AMEX Symbols Count:', query.count()
        
        NYSE_FILE = os.path.join(STOCK_DIR, 'CompanylistNYSE.csv')
        with open(NYSE_FILE, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                symbol = row[0]
                name = row[1]
                if(str.strip(symbol) != '' and str.strip(name) != ''):
                    stock = StockSymbol(symbol = symbol, companyName = name, exchange = 'NYSE')
                    stock.put()
            
            query = StockSymbol.query(StockSymbol.exchange == 'NYSE')
            print 'NYSE Symbols Count:', query.count()