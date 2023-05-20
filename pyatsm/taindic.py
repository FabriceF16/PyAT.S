#!/usr/bin/env python

"""
File name *taindic.py*

Main class to retrieve Technical Analysis Indicators:
- SMA
- Bollinger
- SAR
- etc...

"""

__author__ = "Fabrice F."
__copyright__ = "Copyright 2023, PyAT.S Project"
__credits__ = ["Fabrice F.","TBC Eric, AT.S Association etc..."]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Fabrice F."
__email__ = ""
__status__ = "Development"


import pandas as pd
import numpy as np


class TAindicators():
    """
    Class managing generic technical indicators, like Moving Averages, Bollinger etc...
    """
    def __init__(self,data,limit=True,col='Close'):
        self.limit= limit
        self.col = col
        if limit==True:
            self.data = data.tail(400).copy() #No need to get the full history to calculate indicators, we keep 400 last periods
        else:
            self.data = data.copy()
            self.data_weekly = self.__get_data_period()
            self.data_monthly = self.__get_data_period(period='M')
        return

    #######################################################################################
    # Functions for AT.S: get_ sma, bollinger, psar
    #######################################################################################        
    def get_sma(self,period):
        """ 
        Return data linked with Simple Moving Average, with given period 
        """
        sma = self.data.copy()
        # Generate the moving average data
        sma['sma'] = self.data['Close'].rolling(window=period).mean()
        # Check if the SMA is increasing or decreasing
        sma['sma-1'] = sma['sma'].shift(1)
        #sma = sma.tail(30)
        #print(sma)

        sma['tendance'] = [1 if sma.loc[ei,'sma']> sma.loc[ei,'sma-1'] else -1 for ei in sma.index]
        sma['tendance+1'] = sma['tendance'].shift(-1)
        sma['tendance-1'] = sma['tendance'].shift(1)
        #sma['up'] = [sma.loc[ei,'sma'] if sma.loc[ei,'sma']> sma.loc[ei,'sma-1'] else np.nan for ei in sma.index]
        #sma['dn'] = [sma.loc[ei,'sma'] if sma.loc[ei,'sma']< sma.loc[ei,'sma-1'] else np.nan for ei in sma.index]
        sma['up'] = [sma.loc[ei,'sma'] if (sma.loc[ei,'tendance']==1 and sma.loc[ei,'tendance-1']==1) or (sma.loc[ei,'tendance']==1 and sma.loc[ei,'tendance+1']==1) else np.nan for ei in sma.index]
        sma['dn'] = [sma.loc[ei,'sma'] if (sma.loc[ei,'tendance']==-1 and sma.loc[ei,'tendance-1']==-1) or (sma.loc[ei,'tendance']==-1 and sma.loc[ei,'tendance+1']==-1) else np.nan for ei in sma.index]
        sma['upRev'] = [sma.loc[ei,'sma'] if (sma.loc[ei,'tendance']==-1 and sma.loc[ei,'tendance+1']==1) or (sma.loc[ei,'tendance']==1 and sma.loc[ei,'tendance-1']==-1) else np.nan for ei in sma.index]
        sma['dnRev'] = [sma.loc[ei,'sma'] if (sma.loc[ei,'tendance']==1 and sma.loc[ei,'tendance+1']==-1) or (sma.loc[ei,'tendance']==-1 and sma.loc[ei,'tendance-1']==1) else np.nan for ei in sma.index]
         # Check if price is near the SMA
        sma['distLow'] = (100*(sma['Low']/sma['sma']-1))
        sma['distHigh'] = (100*(sma['sma']/sma['High']-1))
        sma = sma.drop(['Open','High','Low'],axis=1)
        pente_period = 1
        if period>5:
            pente_period = 5
        sma['Pente'] = 100*(sma['sma'].div(sma['sma'].shift(pente_period))-1)
        return sma
    
    def get_bollinger(self,period=20,dev=2.0):
        """
        Return a DataFrame with the Bollinger Up / Middle / Low elements
        """
        u = self.data.copy()
        u['TP'] = (u['Low']+u['High']+u['Close'])/3 
        u['std'] = u['TP'].rolling(20).std(ddof=0)
        u['MA-TP'] = u['TP'].rolling(20).mean()
        u['U'] = u['MA-TP'] + dev*u['std']
        u['U-1'] = u['U'].shift(1)
        u['tendance'] = [1 if u.loc[ei,'U']> u.loc[ei,'U-1'] else -1 for ei in u.index]
        u['tendance+1'] = u['tendance'].shift(-1)
        u['tendance-1'] = u['tendance'].shift(1)
        #u['Uup'] = [u.loc[ei,'U'] if u.loc[ei,'U']> u.loc[ei,'U-1'] else np.nan for ei in u.index]
        #u['Udn'] = [u.loc[ei,'U'] if u.loc[ei,'U']< u.loc[ei,'U-1'] else np.nan for ei in u.index]
        u['Uup'] = [u.loc[ei,'U'] if (u.loc[ei,'tendance']==1 and u.loc[ei,'tendance-1']==1) or (u.loc[ei,'tendance']==1 and u.loc[ei,'tendance+1']==1) else np.nan for ei in u.index]
        u['Udn'] = [u.loc[ei,'U'] if (u.loc[ei,'tendance']==-1 and u.loc[ei,'tendance-1']==-1) or (u.loc[ei,'tendance']==-1 and u.loc[ei,'tendance+1']==-1) else np.nan for ei in u.index]
        u['UupRev'] = [u.loc[ei,'U'] if (u.loc[ei,'tendance']==-1 and u.loc[ei,'tendance+1']==1) or (u.loc[ei,'tendance']==1 and u.loc[ei,'tendance-1']==-1) else np.nan for ei in u.index]
        u['UdnRev'] = [u.loc[ei,'U'] if (u.loc[ei,'tendance']==1 and u.loc[ei,'tendance+1']==-1) or (u.loc[ei,'tendance']==-1 and u.loc[ei,'tendance-1']==1) else np.nan for ei in u.index]
        
        u['L'] = u['MA-TP'] - dev*u['std']
        u['L-1'] = u['L'].shift(1)
        u['tendanceL'] = [1 if u.loc[ei,'L']> u.loc[ei,'L-1'] else -1 for ei in u.index]
        u['tendanceL+1'] = u['tendanceL'].shift(-1)
        u['tendanceL-1'] = u['tendanceL'].shift(1)
        #u['Lup'] = [u.loc[ei,'L'] if u.loc[ei,'L']> u.loc[ei,'L-1'] else np.nan for ei in u.index]
        #u['Ldn'] = [u.loc[ei,'L'] if u.loc[ei,'L']< u.loc[ei,'L-1'] else np.nan for ei in u.index]
        u['Lup'] = [u.loc[ei,'L'] if (u.loc[ei,'tendanceL']==1 and u.loc[ei,'tendanceL-1']==1) or (u.loc[ei,'tendanceL']==1 and u.loc[ei,'tendanceL+1']==1) else np.nan for ei in u.index]
        u['Ldn'] = [u.loc[ei,'L'] if (u.loc[ei,'tendanceL']==-1 and u.loc[ei,'tendanceL-1']==-1) or (u.loc[ei,'tendanceL']==-1 and u.loc[ei,'tendanceL+1']==-1) else np.nan for ei in u.index]
        u['LupRev'] = [u.loc[ei,'L'] if (u.loc[ei,'tendanceL']==-1 and u.loc[ei,'tendanceL+1']==1) or (u.loc[ei,'tendanceL']==1 and u.loc[ei,'tendanceL-1']==-1) else np.nan for ei in u.index]
        u['LdnRev'] = [u.loc[ei,'L'] if (u.loc[ei,'tendanceL']==1 and u.loc[ei,'tendanceL+1']==-1) or (u.loc[ei,'tendanceL']==-1 and u.loc[ei,'tendanceL-1']==1) else np.nan for ei in u.index]

        u = u.drop(['Open','High','Low','TP','std','MA-TP'],axis=1)
        return u      
    
    def get_psar(self, iaf = 0.02, maxaf = 0.2):
        """
        Return the Parabolic SAR, with 1 period of shift (as per AT.S environment)
        """
        facteur=0.02
        increment=0.02
        maxfacteur=0.2
        barsdata = self.data.copy()
        barsdata = barsdata.tail(52)
        
        length = len(barsdata)
        dates = list(barsdata['Date'])
        #dates = list(barsdata.index)
        high = list(barsdata['High'])
        low = list(barsdata['Low'])
        close = list(barsdata['Close'])
        psar = close[0:len(close)]
        psarbull = [None] * length
        psarbear = [None] * length
        
        extreme = [None] * length
        extreme[0] = high[0]
        extreme[1] = high[0]
        tendance = [None] * length
        tendance[0] = 1
        tendance[1] = 1
        tmpSAR = [None] * length
        tmpSAR[0] = low[0]
        tmpSAR[1] = min(low[0],low[1])
        
        i=2
        for i in range(2,length):
            if tendance[i-1]==1:
                extreme[i] = max(extreme[i-1],high[i])
                if tmpSAR[i-1]>low[i]:
                    tendance[i]=-1
                    facteur=0.02
                    tmpSAR[i] = extreme[i]
                    extreme[i] = low[i]
                else:
                    if extreme[i]>extreme[i-1] and facteur<maxfacteur:
                        facteur=min(maxfacteur,facteur+increment)
                    tmpSAR[i]=tmpSAR[i-1]+facteur*(extreme[i]-tmpSAR[i-1])
                    tmpSAR[i]=min(tmpSAR[i],min(low[i],low[i-1]))
                    tendance[i]=1
            elif tendance[i-1]==-1:
                extreme[i]=min(extreme[i-1],low[i])
                if tmpSAR[i-1]<high[i]:
                    tendance[i]=1
                    facteur=0.02
                    tmpSAR[i]=extreme[i]
                    extreme[i]=high[i]
                else:
                    if extreme[i]<extreme[i-1] and facteur<maxfacteur:
                        facteur=min(maxfacteur,facteur+increment)
                    tmpSAR[i]=tmpSAR[i-1]+facteur*(extreme[i]-tmpSAR[i-1])
                    tmpSAR[i]=max(tmpSAR[i],max(high[i],high[i-1]))
                    tendance[i]=-1
            else:
                facteur=0.02
                tmpSAR[i]=low[i]
                extreme[i]=high[i]
                tendance[i]=1
        
        psar = pd.DataFrame({"Date":dates,"Close":close,"tmpSAR":tmpSAR,'tendance':tendance})  
        psar['psar'] = psar['tmpSAR']
        psar['psarbull'] = [psar.loc[ei,'psar'] if psar.loc[ei,'tendance']==1 else np.nan for ei in psar.index]
        psar['psarbear'] = [psar.loc[ei,'psar'] if psar.loc[ei,'tendance']==-1 else np.nan for ei in psar.index]
        
        psar['psarbear-1'] = psar['psarbear'].shift(1)
        psar['psarbull-1'] = psar['psarbull'].shift(1)
        psar['psar-1'] = psar['psar'].shift(1)
        psar = psar.set_index('Date')
        psar['distPSAR'] = (100*(psar['Close']/psar['psar-1']-1))
        #print(psar.tail(25))
        return psar




##############################################################################
### Main section
##############################################################################
if __name__ == '__main__':
    print('Bienvenue dans TA indics!')
    myta = TAindicators()
    