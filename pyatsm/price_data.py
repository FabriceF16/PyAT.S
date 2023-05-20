#!/usr/bin/env python

"""
File name *price_data.py*

Main class to retrieve Price Data:
- AlphaVantage API
etc...

"""

__author__ = "Fabrice F."
__copyright__ = "Copyright 2023, PyAT.S Project"
__credits__ = ["Fabrice F.","TBC Eric, AT.S Association etc..."]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Fabrice F."
__email__ = ""
__status__ = "Development"

KEY_AV = "SMYHWS7HGWBRQ39J"
KEY_DARWINEX = "3539ac22-12dd-3cb5-88c0-1c0ddeb81ce0"

##############################################################################
### IMPORT SECTION
##############################################################################
import argparse, os, time,datetime
import pandas as pd
from datetime import date, datetime, timedelta
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, './pyatsm/')
from taindic import TAindicators
#from cnopy.taindic import TAindicators

#for Darwinex
import requests
import json
from pandas import json_normalize



##############################################################################
### GLOBAL VARIABLES AND FUNCTIONS
##############################################################################
START_TIME = time.time() # for performance tracking
def print_duration():
    """      
    :return: Time duration of the script execution, to be printed
    """
    dur = time.time() - START_TIME
    if dur > 60:
        string_dur = " --- %s minutes ---" % (round(dur/60,2))
    else:
        string_dur = " --- %s seconds ---" % (round(dur,2))
    return string_dur


class StockYFdata():
    """
    Class which extract Yahoo Finance data for one stock
    """
    def __init__(self,ticker, daily=True):
        self.ticker = ticker
        self.riskfree_rate = 0
        self.daily = daily

        data_folder = "./data/"
        CURRENT_PATH=os.getcwd()
        if CURRENT_PATH.find('pyatsm')>0:
            data_folder = "../data/"
        if daily==True:
            self.yf_path = data_folder+self.ticker+'.csv'
        else:
            self.yf_path = data_folder+self.ticker+"_monthly.csv"
        return
        
    def __test_history_file(self):
        """
        Test if Yahoo Finance data is already downloaded and up to date
        
        :return: 0 if file up to date, -1 if download needed
        """
        status = -1
        data_file = self.yf_path
        if os.path.exists(data_file):
            data = pd.read_csv(data_file,index_col='Date',parse_dates=['Date'])
            data['Date'] = data.index
            self.data = data.copy()
            last_date = data.tail(1).index.item()
            last_date = last_date.date()
            presentDate = date.today()
            if (presentDate-last_date).days <2:
                print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
            elif (presentDate-last_date).days < 3 and date.today().weekday() == 6:
                print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
            elif (presentDate-last_date).days < 4 and date.today().weekday() == 0:
                print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
        return status

    def web_open_yf(self,daily=True,replace=False,wait=1):
        """
        Open url in a new tab in Chrome 
        """
        yf_path = self.yf_path
        year_current, month = time.strftime("%Y,%m").split(',')
        presentDate = datetime.today()
        period2=str(int(datetime.timestamp(presentDate)))
        period1=str(int(datetime.timestamp(presentDate-timedelta(days=25*365+30))))
        
        if daily==True:
            url="https://finance.yahoo.com/quote/"+self.ticker+"/history?period1="+period1+"&period2="+period2+"&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
        else:
            url="https://finance.yahoo.com/quote/"+self.ticker+"/history?period1="+period1+"&period2="+period2+"&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true"
     
        #Download 
        if self.__test_history_file() < 0:
            query_string = "https://query1.finance.yahoo.com/v7/finance/download/"+self.ticker+"?period1="+period1+"&period2="+period2+"&interval=1d&events=history&includeAdjustedClose=true"
            #print(query_string)
            df=pd.read_csv(query_string)
            df.set_index("Date")
            df.to_csv(self.yf_path,index=False)
            print("Downloading "+str(len(df))+" data for "+self.ticker+" in file "+self.yf_path+print_duration())
            print('Waiting period (s): '+str(wait))
            time.sleep(wait)
        
        return

    def __get_data(self):
        #if os.path.exists(data_file) and conn==None:
        data = pd.read_csv(self.yf_path,index_col='Date',parse_dates=['Date'])
        data['Date'] = data.index
        return data



class AlphaVantageData():
    """
    Class which extract Alphavantage.co data for one stock
    """
    def __init__(self,ticker,intra=False):
        self.key_av = KEY_AV
        self.ticker = ticker

        data_folder = "./data/"
        CURRENT_PATH=os.getcwd()
        if CURRENT_PATH.find('pyatsm')>0:
            data_folder = "../data/"
        if intra==False:
            self.av_path = data_folder+self.ticker+'.csv'
        else:           
            self.av_path = data_folder+self.ticker+'_intra.csv'
        return

    def __test_history_file(self):
        """
        Test if Alphavantage data is already downloaded and up to date
        
        :return: 0 if file up to date, -1 if download needed
        """
        status = -1
        data_file = self.av_path
        if os.path.exists(data_file):
            data = pd.read_csv(data_file,index_col='Date',parse_dates=['Date'])
            data['Date'] = data.index
            self.data = data.copy()
            last_date = data.tail(1).index.item()
            last_date = last_date.date()
            presentDate = date.today()
            if (presentDate-last_date).days <2:
                #print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
            elif (presentDate-last_date).days < 3 and date.today().weekday() == 6:
                #print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
            elif (presentDate-last_date).days < 4 and date.today().weekday() == 0:
                #print("File already exists "+data_file+" - "+str(last_date)+print_duration())
                status=0
        return status
    
    def av_daily_download(self,wait=0):
        """
        Download Alphavantage data from Symbol
        """
        
        if self.__test_history_file() == 0:
            return 0 #File already exist, no download needed
        
        
        symbol = self.ticker
        symbol_query = 'symbol='+symbol
        #function_query='TIME_SERIES_DAILY' => became premium
        function_query='TIME_SERIES_DAILY_ADJUSTED'
        #new_cols = ["Date","Open","High","Low","Close","Volume"]
        new_cols = ["Date","Open","High","Low","Close","AdjustedClose","Volume","Dividend","Split"]
        if symbol.find('-')>0:
            symbol_query='from_symbol='+symbol.split('-')[0]+'&to_symbol='+symbol.split('-')[1]
            function_query='FX_DAILY'
            new_cols = ["Date","Open","High","Low","Close"]
       
        url = 'https://www.alphavantage.co/query?function='+function_query+'&'+symbol_query+'&outputsize=full&apikey='+self.key_av
        url_csv = url+'&datatype=csv'
        #print(url_csv)
        try:
            df=pd.read_csv(url_csv)
            #print(df.head(10))
        except:
            print("ERROR: issue with download for: "+self.ticker)
            return -1
            
        try:
            df.columns = new_cols
        except:
            print("WARNING: issue with data file for: "+self.ticker)
            print(df.head(0))
            return -1
        df = df.sort_values(by="Date")
       
        #print(df)
        df.set_index("Date")
        df.to_csv(self.av_path,index=False)
        print("Downloading "+str(len(df))+" data for "+self.ticker+" in file "+self.av_path+print_duration())
        if wait>0:
            print('Waiting period (s): '+str(wait))
            time.sleep(wait)
        return 0 
    
    def av_intraday_download(self):
        """
        Download Alphavantage intraday data from Symbol
        """
        
        ### TO BE REMOVED ###
        if self.__test_history_file() == 0:
            return #File already exist, no download needed
        ###
        
        symbol = self.ticker
        symbol_query = 'symbol='+symbol
        function_query='TIME_SERIES_INTRADAY'
        new_cols = ["Date","Open","High","Low","Close","Volume"]
        if symbol.find('-')>0:
            symbol_query='from_symbol='+symbol.split('-')[0]+'&to_symbol='+symbol.split('-')[1]
            function_query='FX_INTRADAY'
            new_cols = ["Date","Open","High","Low","Close"]
            
        url = 'https://www.alphavantage.co/query?function='+function_query+'&'+symbol_query+'&interval=5min&outputsize=full&apikey='+self.key_av
        url_csv = url+'&datatype=csv'
        
        df=pd.read_csv(url_csv)
        #print(df)
        df.columns = new_cols
        df = df.sort_values(by="Date")
        df.set_index("Date")
        df.to_csv(self.av_path,index=False)
        print("Downloading "+str(len(df))+" data for "+self.ticker+" in file "+self.av_path)
        return

    def __get_data(self):
        #if os.path.exists(data_file) and conn==None:
        data = pd.read_csv(self.av_path,index_col='Date',parse_dates=['Date'])
        data['Date'] = data.index
        return data


class Darwinex():
    """
    Class enabling to interact with Darwinex
    """
    
    def __init__(self):
        self.token = KEY_DARWINEX
        self.dba_folder = "./data/"
        CURRENT_PATH=os.getcwd()
        if CURRENT_PATH.find('pyatsm')>0:
            self.dba_folder = "../data/"
            #print(self.dba_folder)
        return
    
    def download_dba(self,product="DBA"):
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer "+self.token,
            #'authorization': self.token,
        }
        
        year_current, month = time.strftime("%Y,%m").split(',')
        presentDate = datetime.today()
        period2=str(int(datetime.timestamp(presentDate)))
        period1=str(int(datetime.timestamp(presentDate-timedelta(days=25*365+30))))
        url = f'https://api.darwinex.com/darwininfo/2.1/products/{product}/candles?resolution=1d&from='+period1+'&to='+period2
        #url = f'https://api.darwinex.com/darwininfo/2.1/products/{product}/candles/ALL?resolution=1d'
        print(url)
        response = requests.get(url, headers=headers)
        data = response.json()
        
        #print(data)
        #if 'Invalid Credentials' in data.values():
        #    print('WARNING: Invalid Credentials')
        df = pd.DataFrame(data['candles'])
        values = json_normalize(df['candle'])
        values['timestamp'] = df['timestamp']
        #values['Date'] = pd.to_datetime(values['timestamp'], unit='s').dt.date
        values['Date'] = pd.to_datetime(values['timestamp'], unit='s')
        values['DateNew'] = (values['Date']+ pd.Timedelta('1 day')).dt.date
        values = values.drop(columns=['timestamp','Date'],axis=1)
        values.columns = ['Close','High','Low','Open','Date']
        values = values[["Date","Open","High","Low","Close"]]
        values = values.iloc[1:, :]
        
        
        dba_init = pd.read_csv(self.dba_folder+"dba_init.csv", delimiter=',', on_bad_lines='skip')
        if product=="DBA":
            values = dba_init.append(values,ignore_index=True)
        
        values.set_index("Date")
        values.to_csv(self.dba_folder+product.lower()+'.csv',index=False)
        
        return

    def download_jtl(self,product="JTL"):
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer "+self.token,
            #'authorization': self.token,
        }
        dfs = []
        # Collect data for ALL and 1Y
        for dur in ['ALL','1Y']:
            url = f'https://api.darwinex.com/darwininfo/2.1/products/{product}/candles/{dur}?resolution=1d'
            print(url)
            response = requests.get(url, headers=headers)
            data = response.json()
            #Convert Json into Dataframe
            df = pd.DataFrame(data['candles'])
            values = json_normalize(df['candle'])
            values['timestamp'] = df['timestamp']
            values['Date'] = pd.to_datetime(values['timestamp'], unit='s')
            values['DateNew'] = (values['Date']+ pd.Timedelta('1 day')).dt.date
            values = values.drop(columns=['timestamp','Date'],axis=1)
            values.columns = ['Close','High','Low','Open','Date']
            values = values[["Date","Open","High","Low","Close"]]
            values = values.iloc[1:, :]

            values.set_index("Date")
            values.to_csv(self.dba_folder+product+'_'+dur+'.csv',index=False)
            dfs.append(values)

        #Concatenate Dataframes to create 1 csv file only, removing duplicates
        df = pd.concat(dfs)
        df = df.sort_values(by="Date",ascending=True)
        df = df.drop_duplicates(subset='Date', keep="last")
        df.set_index("Date")
        df.to_csv(self.dba_folder+product.lower()+'.csv',index=False) # save into a csv file

        return 0






##############################################################################
### Main section
##############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",dest='ticker', help="Download data for Ticker")
    args = parser.parse_args()

    print('Bienvenue dans Price Data!')
