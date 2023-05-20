#!/usr/bin/env python

"""
File name *pyats.py*

All functions to plot data in graphs for visualization
Using AT.S Environment
"""

__author__ = "Fabrice F."
__copyright__ = "Copyright 2023, PyAT.S Project"
__credits__ = ["Fabrice F.","TBC Eric, AT.S Association etc..."]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Fabrice F."
__email__ = ""
__status__ = "Development"


##############################################################################
### IMPORT SECTION
##############################################################################
import argparse, os, time,datetime
import pandas as pd
import numpy as np
from datetime import datetime,timedelta,date

import plotly.graph_objects as go
from plotly.subplots import make_subplots


from pyatsm.price_data import AlphaVantageData, Darwinex, StockYFdata
from pyatsm.taindic import TAindicators



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

##############################################################################
### CLASSES SECTION
##############################################################################

class EnvATS():
    """ 
    Class managing the Graphical Environment of asset with AT.S indicators
    """
    def __init__(self,symbol="", name="", pur=False,ut=None,date_sig=None,intra=False,filename=None):
        self.status = 1
        self.symbol = symbol
        self.name = name
        self.intraday = False
        self.periods = ['D','W','1M','Q','2Q','Y']
        self.distances = [0.3,0.5,1,1,1,5]
        av = False # test AV ticker
        dw = False # Test Darwinex ticker (DBA)
        kwcbo = False # Test Darwinex KWCBO ticker (KWCBO)

        if symbol.find('.') > 0:
            if symbol.split('.')[1] in ['PAR','BRU','AMS','BSE']: #Test symbol extension for Alphavantage
                av = True
        elif symbol.find('-') > 0: # Test Forex symbol
            av = True
        elif symbol in ['DBA', 'KWCBO', 'JTL']:
            dw = True

        data_folder = "./data/"
        CURRENT_PATH=os.getcwd()
        if CURRENT_PATH.find('pyatsm')>0:
            data_folder = "../data/"
        if filename != None:
            data_file = filename
        else:
            data_file = data_folder+symbol+'.csv'

        if os.path.exists(data_file):
            print('INFO: Reading data file: '+data_file)
            data = pd.read_csv(data_file,index_col='Date',parse_dates=['Date'])
            data['Date'] = data.index
            try:
                data = data.drop('Volume',axis=1)
            except:
                print('WARNING: no column Volume')
            self.data = data.copy()
            last_date = data.tail(1).index.item()
            last_date = str(last_date.date())       
        else:
            print('WARNING: file does not exist: '+data_file)
            self.status = 0
            return
        self.last_date = last_date
        self.ut = ''
        if ut != None:
            self.img_file = "png/"+symbol+'_'+last_date+"_"+ut+".png"
            self.fig = self.__initiate_fig_ut(ut)
            self.ut = ut
        elif intra == True:
            self.img_file = "png/"+symbol+'_intra_'+last_date+".png"
            self.intraday = True
            self.periods = ['5min','15min','30min','1H','3H','D']
            self.fig = self.__initiate_fig()  
        else:
            self.img_file = "png/"+symbol+'_'+last_date+".png"
            self.fig = self.__initiate_fig()
        self.pur = pur # Ensure that there are no annotations on graphs
        self.date_sig = ''
        if date_sig != None:
            self.date_sig = date_sig
        return
    
    def __set_data_file(self):
        ''' TODO '''
        data_file = ""
        symbol = self.symbol

        return data_file

    def __initiate_fig(self):
        """ 
        Initialize a Plotly figure with 6 subplots 
        
        :return: Plotly fig to be enriched and shown
        """
        symbol = self.symbol
        subtitles = []
        for period in self.periods:
            subtitles.append(symbol+' -'+period)
        
        fig = make_subplots(rows=2, cols=3,
                subplot_titles=(subtitles[0],subtitles[1],subtitles[2],subtitles[5],subtitles[4],subtitles[3]),
                horizontal_spacing = 0.05,vertical_spacing = 0.1)       
        return fig
    
    def __initiate_fig_ut(self,ut):
        """ Initialize a Plotly figure with 1 subplot """
        symbol = self.symbol
        fig = make_subplots(rows=1, cols=1,
            subplot_titles=[symbol+' -'+ut])
        return fig

    def __get_row_col_ids(self,period="D"):
        """ Return row and column ID depending on period """
        row_col = [1,1,0.3]
        UTs = pd.DataFrame({'Period':self.periods,
                            'Row':[1,1,1,2,2,2],
                            'Col':[1,2,3,3,2,1],
                            'Dist':self.distances,
                            }).set_index('Period')
        if period in UTs.index:
            row_col = [UTs['Row'].loc[period],UTs['Col'].loc[period],UTs['Dist'].loc[period]]     
        return row_col

    def get_fig(self):
        """ Return fig class attribute for external access """
        return self.fig
    
    def get_data(self):
        """ Return data class attribute for external access """
        return self.data

    def get_img(self):
        return self.img_file

    def get_status(self):
        """ Return status class attribute for external access """
        return self.status
        
    def create_ats_view(self):
        """ Create the full AT.S view for 1 symbol, using CSV data """
        fig = self.fig

        # Logic to create other timeframes, than the data file
        logic = {'Open'  : 'first',
                 'High'  : 'max',
                 'Low'   : 'min',
                 'Close' : 'last'} 
        # Create the UTs for each period
        for period in self.periods:
            df = self.data.copy()
            if period != 'D':
                df = df.resample(period,convention='end',closed='right',label='right').apply(logic)
                # if period != 'W': # TO REMOVE - bug later in the graph creation
                #     df.index = df.index.to_period('M')
                df['Date'] = df.index
                #print(df.tail(10))
            fig = self.__create_ut(df,period)
            if period == 'D':
                fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],rangeslider_visible=False,row=1,col=1)       
            if self.pur == False:
                fig = self.__create_annotations(df,period)
        
        last_date = self.data.tail(1).index.item()
        last_date = str(last_date.date())
        fig.update_layout(
            title=self.symbol+' - '+self.name+' - '+last_date,
            height=800, width=1200,
            #yaxis_title='Price',
        )
               
        fig.write_image(self.img_file,width=1200,height=800)
        fig.write_image("static/"+self.img_file,width=1200,height=675) #For Flask
        print("Image saved for static/"+self.img_file+print_duration())
        
        return fig

    def create_ats_view_intraday(self):
        fig = self.fig
        
        #M5 timeframe        
        df_m5 = self.data.copy()         
        fig = self.__create_ut(df_m5,1,1)
                
        # Other timeframes
        logic = {'Open'  : 'first',
                 'High'  : 'max',
                 'Low'   : 'min',
                 'Close' : 'last'}
        UTs = pd.DataFrame({'Period':['15min','30min','1H','3H','D'],
                            'Row':[1,1,2,2,2],
                            'Col':[2,3,3,2,1],
                            })
        UTs = UTs.set_index('Period')
        
        for period in UTs.index:
            df = self.data.copy()
            df = df.resample(period,convention='start').apply(logic)
            df['Date'] = df.index
            fig = self.__create_ut(df,UTs['Row'].loc[period],UTs['Col'].loc[period])
            if self.pur == False:
                fig = self.__create_annotations(df,UTs['Row'].loc[period],UTs['Col'].loc[period],distance=1)
        
        last_date = self.data.tail(1).index.item()
        last_date = str(last_date.date())
        fig.update_layout(
            title=self.symbol+' - '+self.name+' - '+last_date,
            #yaxis_title='Price',
        )
     
        fig.write_image(self.img_file,width=1200,height=800)
        print("Image saved for "+self.symbol)
        
        return fig
    
    def __create_ut(self,data,period):
        """ Create ATS UT view for 1 symbol """
        fig = self.fig
        df_d = data.copy()
        ta = TAindicators(df_d)
        #print(period)
        m7d = ta.get_sma(7).tail(25)
        #m7d = ta.get_sma(7)
        md = ta.get_sma(20).tail(25)
        boll_d = ta.get_bollinger().tail(25)
        df_d = df_d.tail(25)
          
        row_col = self.__get_row_col_ids(period)
        i_row = row_col[0]
        i_col = row_col[1]
        boll_trace = pd.DataFrame({
                    'Col':['U','Uup','Udn','UupRev','UdnRev','L','Lup','Ldn','LupRev','LdnRev'],
                    'Color':['black','green','red','green','red','black','green','red','green','red'],
                    'Width':[1,2,2,2,2,1,2,2,2,2],
                    }).set_index('Col')
        
        sma_trace = pd.DataFrame({
                    'Col':['sma','up','dn','upRev','dnRev'],
                    'Color':['black','green','red','green','red'],
                    'Width':[1,2,2,2,2],
                    }).set_index('Col')            
        fig = fig.add_trace(go.Ohlc(x=df_d.index,open=df_d['Open'],high=df_d['High'],low=df_d['Low'],close=df_d['Close'],increasing_line_color= 'black', decreasing_line_color= 'black',showlegend=False),row=i_row,col=i_col)
        for col in sma_trace.index:
            fig.add_trace(go.Scatter(x=df_d.index,y=m7d[col],mode='lines',line=dict(color=sma_trace['Color'].loc[col],width=sma_trace['Width'].loc[col]),
                showlegend=False),row=i_row,col=i_col)
            #fig.add_trace(go.Scatter(x=df_d.index,y=m7d[col],mode='markers',marker_color=sma_trace['Color'].loc[col],
            #    showlegend=False),row=i_row,col=i_col)
            fig.add_trace(go.Scatter(x=df_d.index,y=md[col],mode='lines',line=dict(color=sma_trace['Color'].loc[col],width=sma_trace['Width'].loc[col]),
                showlegend=False),row=i_row,col=i_col)       
        for col in boll_trace.index:
            fig.add_trace(go.Scatter(x=df_d.index,y=boll_d[col],mode='lines',line=dict(color=boll_trace['Color'].loc[col],width=boll_trace['Width'].loc[col]),
                showlegend=False),row=i_row,col=i_col)

        #if sar_ok == True:
        try:
            psar_d = ta.get_psar().tail(25)
            fig.add_trace(go.Scatter(x=df_d.index,y=psar_d['psarbull-1'],mode='markers',marker_color='green',showlegend=False),row=i_row,col=i_col)
            fig.add_trace(go.Scatter(x=df_d.index,y=psar_d['psarbear-1'],mode='markers',marker_color='red',showlegend=False),row=i_row,col=i_col)
            #if period == '2Q':
            #    print('SAR for: '+period)
            #    print(df_d)
            #    print(psar_d.tail(30))
        except:
            print('WARNING: issue with SAR on period '+period)
        

        # DEBUG 
        #if period == 'W':
            #print(m7d)
            #print(md)
            #print(boll_d)
        #    print(psar_d)

        # Annotations
        if not self.pur:
            extra = EnvATSextraUT(fig,df_d,row_col)
            fig = extra.create_annotations()


        fig.update_xaxes(rangeslider_visible=False,row=i_row,col=i_col)
        for period in [8,21]:
            if df_d.index.size>period:
                fig.add_vline(x=df_d.index[-period], line_width=2, line_dash="dash", line_color="black",row=i_row,col=i_col)

        return fig
        
    def __create_annotations(self,data,period="D"):
        """ Add annotations (supports / resistance etc...) to graph, for 1 UT """
        fig_a = self.fig
        df_d = data.copy()        
        ta = TAindicators(df_d)
        m7d = ta.get_sma(7)
        md = ta.get_sma(20)
        boll_d = ta.get_bollinger()
        try:
            psar_d = ta.get_psar()
            psar_d = psar_d.tail(1)
            sar_ok = True
        except:
            #print('WARNING: issue with SAR on period '+period)
            sar_ok= False
        df_d = df_d.tail(25)
        m7d = m7d.tail(1)
        md = md.tail(1)
        boll_d = boll_d.tail(2)
        #print(psar_d)
        
        #print(df_d)
        last = df_d['Close'].tail(1).iloc[0]
        high = df_d['High'].tail(1).iloc[0]
        low = df_d['Low'].tail(1).iloc[0]
        jack = df_d['Close'].tail(21).iloc[0]
        df_d["Jack"] = jack
        #print(oggy)
               
        row_col = self.__get_row_col_ids(period)                        
        distance = row_col[2]
        nb_sup = 0
        nb_res = 0
        
        ### M7 ###
        if m7d['up'].iloc[0]>0 and abs(m7d['distLow'].iloc[0])<distance: #Support
            print('M7 support on period '+period)
            nb_sup = nb_sup+1
            if nb_sup < 2:
                fig_a.add_annotation(x=m7d["Date"].iloc[0], y=m7d['sma'].iloc[0]*(1-distance/100),
                    showarrow=True,ax=0,ay=20,arrowwidth=2,arrowhead=1,arrowcolor="green",
                    row=row_col[0],col=row_col[1])  
        
        if m7d['dn'].iloc[0]>0 and abs(m7d['distHigh'].iloc[0])<distance: #Resistance
            print('M7 resistance on period '+period)
            nb_res = nb_res+1
            if nb_res < 2:
                fig_a.add_annotation(x=m7d["Date"].iloc[0], y=m7d['sma'].iloc[0]*(1+distance/100),
                    showarrow=True,ax=0,ay=-20,arrowwidth=2,arrowhead=1,arrowcolor="red",
                    row=row_col[0],col=row_col[1]) 
        
        ### M ###
        if md['up'].iloc[0]>0 and abs(md['distLow'].iloc[0])<distance: #Support
            print('M support on period '+period) 
            fig_a.add_annotation(x=md["Date"].iloc[0], y=md['sma'].iloc[0]*(1-distance/100),
                showarrow=True,ax=0,ay=20,arrowwidth=2,arrowhead=1,arrowcolor="green",
                row=row_col[0],col=row_col[1]) 
                
        if md['dn'].iloc[0]>0 and abs(md['distHigh'].iloc[0])<distance: #Resistance
            print('M resistance on period '+period)
            fig_a.add_annotation(x=md["Date"].iloc[0], y=md['sma'].iloc[0]*(1+distance/100),
                showarrow=True,ax=0,ay=-20,arrowwidth=2,arrowhead=1,arrowcolor="red",
                row=row_col[0],col=row_col[1])



        #### Supports
        if sar_ok == True:
            if psar_d['psarbull-1'].iloc[0]>0 and abs(psar_d['distPSAR'].iloc[0])<distance:
                print('P support on period '+period)
                fig_a.add_annotation(x=psar_d.index.item(), y=psar_d['psarbull-1'].iloc[0]*(1-distance/100),
                    text="P "+str(round(psar_d['distPSAR'].iloc[0],1))+"%", showarrow=True,ax=0,ay=20,arrowwidth=2,
                    arrowhead=1,row=row_col[0],col=row_col[1])
                
        ### Resistances
        
        return fig_a
    
    def __extra_oggy(self,data,period="D",nb_sup=0,nb_res=0):
        """
        TO REMOVE - Create annotations around Oggy
        """
        fig_a = self.fig
        df_d = data.copy() 
        last = df_d['Close'].tail(1).iloc[0]
        high = df_d['High'].tail(1).iloc[0]
        low = df_d['Low'].tail(1).iloc[0]
        oggy = df_d['Close'].tail(8).iloc[0]
        oggy_1 = df_d['Close'].tail(7).iloc[0]
        oggy_2 = df_d['Close'].tail(6).iloc[0]
        df_d["Oggy"] = oggy

        row_col = self.__get_row_col_ids(period)                        
        distance = row_col[2]

        if last<oggy and low<oggy and abs(100*(oggy/high-1))<distance: #Resistance
            print('O resistance on period '+period)
            nb_res = nb_res+1
            if nb_res < 2:
                fig_a.add_annotation(x=md["Date"].iloc[0], y=oggy*(1+distance/100),
                    showarrow=True,ax=0,ay=-20,arrowwidth=2,arrowhead=1,arrowcolor="red",
                    row=row_col[0],col=row_col[1])
            fig_a.add_trace(go.Scatter(x=df_d.tail(8).index,y=df_d['Oggy'].tail(8),mode='lines',line=dict(color="blue",width=2),
                showlegend=False),row=row_col[0],col=row_col[1])            
        

        if last>oggy and low>oggy and abs(100*(low/oggy-1))<distance: #Support
            print('O support on period '+period)
            nb_res = nb_res+1
            if nb_res < 2:
                fig_a.add_annotation(x=md["Date"].iloc[0], y=oggy*(1-distance/100),
                    showarrow=True,ax=0,ay=20,arrowwidth=2,arrowhead=1,arrowcolor="green",
                    row=row_col[0],col=row_col[1])
            fig_a.add_trace(go.Scatter(x=df_d.tail(8).index,y=df_d['Oggy'].tail(8),mode='lines',line=dict(color="blue",width=2),
                showlegend=False),row=row_col[0],col=row_col[1])

        return [fig_a,nb_sup,nb_res]   
    
    def __create_signal(self,data,i_row,i_col):
        """
        TO REMOVE
        """
        fig_a = self.fig
        df_d = data.copy()
        if self.date_sig != '':
            #print(df_d[df_d['Date']==self.date_sig])
            df_d = df_d[df_d['Date']==self.date_sig]
            fig_a.add_annotation(x=df_d.index.item(), y=df_d['Low'].iloc[0]*(1-0.3/100),
                text="S", showarrow=True,ax=0,ay=20,arrowwidth=2,
                arrowhead=1,row=i_row,col=i_col)
            
        return fig_a

class EnvATSextraUT():
    ''' TODO add annotations in a UT (Timeframe in French) '''
    def __init__(self,fig,df,row_col):
        self.fig = fig # Global plotly figure
        self.row_col = row_col # Row and Column of UT in figure
        self.i_row = row_col[0]
        self.i_col = row_col[1]
        self.df = df.copy() # Data history OHLC of the UT
        self.nb_sup = 0 # Number of supports on the graph
        self.nb_res = 0 # Number of resistances on the graph
        return

    def create_annotations(self):
        fig = self.__oggy_in_between()
        fig = self.__jack_in_between()
        return fig

    def __oggy_in_between(self):
        ''' Print O,O+1,O+2 if last is in between '''
        df_d = self.df.copy()
        last = df_d['Close'].tail(1).iloc[0]
        oggy = df_d['Close'].tail(8).iloc[0]
        oggy_1 = df_d['Close'].tail(7).iloc[0]
        oggy_2 = df_d['Close'].tail(6).iloc[0]
        df_d["Oggy"] = oggy
        df_d["Oggy_1"] = oggy_1
        df_d["Oggy_2"] = oggy_2

        if min(oggy,oggy_1) < last < max(oggy,oggy_1):
            self.fig.add_trace(go.Scatter(x=df_d.tail(8).index,y=df_d['Oggy'].tail(8),mode='lines',line=dict(color="blue",width=2),
                showlegend=False),row=self.row_col[0],col=self.row_col[1])
            self.fig.add_trace(go.Scatter(x=df_d.tail(7).index,y=df_d['Oggy_1'].tail(7),mode='lines',line=dict(color="blue",width=2),
                showlegend=False),row=self.row_col[0],col=self.row_col[1])
            #self.fig.add_trace(go.Scatter(x=df_d.tail(6).index,y=df_d['Oggy_2'].tail(6),mode='lines',line=dict(color="blue",width=2),
            #    showlegend=False),row=self.row_col[0],col=self.row_col[1])      

        return self.fig

    def __jack_in_between(self):
        ''' Print J,J+1,J+2 if last is in between '''
        df_d = self.df.copy()
        last = df_d['Close'].tail(1).iloc[0]
        jack = df_d['Close'].tail(21).iloc[0]
        jack_1 = df_d['Close'].tail(20).iloc[0]
        jack_2 = df_d['Close'].tail(19).iloc[0]
        df_d["Jack"] = jack
        df_d["Jack_1"] = jack_1
        df_d["Jack_2"] = jack_2

        if min(jack,jack_1) < last < max(jack,jack_1):
            self.fig.add_trace(go.Scatter(x=df_d.tail(21).index,y=df_d['Jack'].tail(21),mode='lines',line=dict(color="green",width=2),
                showlegend=False),row=self.row_col[0],col=self.row_col[1])
            self.fig.add_trace(go.Scatter(x=df_d.tail(20).index,y=df_d['Jack_1'].tail(20),mode='lines',line=dict(color="green",width=2),
                showlegend=False),row=self.row_col[0],col=self.row_col[1])
            #self.fig.add_trace(go.Scatter(x=df_d.tail(18).index,y=df_d['Jack_2'].tail(18),mode='lines',line=dict(color="green",width=2),
            #    showlegend=False),row=self.row_col[0],col=self.row_col[1])      

        return self.fig
       

class Ticker():
    ''' TODO Ticker '''

    def __init__(self,symbol, name="",type_ticker=""):
        self.symbol = symbol 
        self.name = name
        self.type_ticker = type_ticker
        return

    def download_data_from_ticker(self,no_download=False):
        ''' Download price data if needed, from different sources: Darwinex, YahooFinance, Alphavantage
        Generates stats (technical indicators)
        '''
        status = -1
        symbol = self.symbol
        if symbol == 'DBA':
            dba = Darwinex()
            dba.download_dba(symbol)
            status = 0
        elif symbol == 'JTL':
            dba = Darwinex()
            dba.download_jtl(symbol)
            status = 0
        elif symbol == 'KWCBO':
            print('WARNING: data to retrieve manually for '+symbol)
            dba = Darwinex()
            dba.open_kwcbo()
        elif symbol.find('.')>0:
            if symbol.split('.')[1] in ['PAR','BRU','AMS','BSE']: #Test symbol extension for Alphavantage
                stock_av = AlphaVantageData(symbol)
                if no_download == False:
                    stock_av.av_daily_download()
            else:
                print(f'Downloading {symbol} from YahooFinance')            
                stock_yf = StockYFdata(symbol)
                stock_yf.web_open_yf()
        else:
            print(f'Downloading {symbol} from YahooFinance')            
            stock_yf = StockYFdata(symbol)
            stock_yf.web_open_yf()
        status = 0
        # else:
        #     print('WARNING: symbol not accepted - '+symbol)
        return status

    def launch_ats_view(self,pur=False):
        s_env = EnvATS(self.symbol,self.name,pur)
        if s_env.get_status() == 1:
            fig = s_env.create_ats_view()            
            fig.show()

        self.s_env = s_env
        return s_env


##############################################################################
### Main section
##############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",dest='ticker', help="Generates AT.S view for YF or AV Ticker")
    parser.add_argument("-f",dest='file', help="Generates AT.S view from the CSV file ")
    
    extras = parser.add_argument_group('Extras options')    
    extras.add_argument("--name",dest='name', help="Add the name of the asset")
    extras.add_argument("--no_download",dest='no_download', action='store_true', help="Directly use local data without downloading fresh one")  
    extras.add_argument("--pur",dest='pur', action='store_true', help="Ensure that there are no annotations on graph")
      
        
    args = parser.parse_args()
    

    symbol = ""
    name = ""
    if args.name != None:
        name = args.name
    ### -t <YFticker> or <AVticker>
    if args.ticker!=None:
        ticker = Ticker(args.ticker,name=name)
        if not args.no_download:
            #print('TEST')
            ticker.download_data_from_ticker()
        ticker.launch_ats_view(args.pur) #Generate AT.S view and save PNG 

    elif args.file != None:
        s_env = EnvATS(name=name,filename=args.file,pur=args.pur)
        if s_env.get_status() == 1:
            fig = s_env.create_ats_view()            
            fig.show()




            
            