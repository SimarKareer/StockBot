# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import pyEX
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import heapq
import psutil
import os
import json

# %%
with open("config.json") as f:
  key = json.load(f)

c = pyEX.Client(key["TOKEN"])
c.symbolsDF().head()

idf = c.intradayDF("AAPL")

idf2 = pd.read_csv("IEX_historical-prices/script/output/2020/2020-CW09/20200224/DONE/20200224_LYFT.csv")
idf2.drop(columns="Unnamed: 0", inplace=True)
idf2.head()

idf.head()

idf["date"]

# %%
def decisionLoop(tradingSession):
    """
        make a function which I can call, each time with all relevant time series up to the correct date.
        Pass in the current state holding object (something keeping track of all the portfolios and individual stocks I have)
        
    """
    print("Currently have $", tradingSession.money, "in cash")
    tradingSession.buy("LYFT", 1)
    tradingSession.buy("MSFT", 1)
    tradingSession.buy("DBX", 1)
    tradingSession.buy("FB", 1)
    # tradingSession.buy("YELP", 1)
    print("Net value at ", tradingSession.time, " is ", tradingSession.value())
    print("--------------------")


# %%
def runDecisionLoop(start, end, timestep, decisionLoop):
    """
        given a time period, start to end, run the algorithm implemented in decision loop for each provided timestep
        Args:
            start - datetime
            end - datetime
            timestep - timedelta
            decisionLoop - function to decide how to make decision
    """
    market = Market()
    ts = TradingSession(None, 1000000, market, start)
    print("starting with", ts.money)
    while ts.time < end:
        decisionLoop(ts)
        ts.updateTime(timestep)
    ts.end()

start = datetime.strptime("2020-02-24 09:30", "%Y-%m-%d %H:%M")
end = start + timedelta(hours = 2)
runDecisionLoop(start, end, timedelta(minutes = 1), decisionLoop)
    

# %%
"""
    A trading session keeps track of all the stocks and portfolios you've bought, and at what price you bought them.
    Keeps track of current time, and won't allow you to access any data beyond your current time.
"""
class TradingSession:
    def __init__(self, logLocation, money, market, time):
        self.stocksOwned = {}
        self.logLocation = logLocation
        self.initMoney = money
        self.money = money
        self.market = market
        self.time = time
    
    def end(self):
        #TODO: saves output log file
        print("Finished Session with final value of $", self.value())

    def buy(self, ticker, quantity):
        # adds smaller information into log string
        #ex) AAPL, 10, $100, time
        if self.market.getPrice(ticker, self.time) is None:
            return

        if ticker in self.stocksOwned:
            self.stocksOwned[ticker] += quantity
        else:
            self.stocksOwned[ticker] = quantity
        #TODO: UPDATE netvalue

        print("Bought at price: ", self.market.getPrice(ticker, self.time))
        self.money -= quantity * self.market.getPrice(ticker, self.time)
    
    def sell(self, ticker, quantity):
        if self.market.getPrice(ticker, self.time) is None:
            return
        self.stocksOwned[ticker] -= quantity
        self.money += quantity * self.market.getPrice(ticker, self.time)
    
    def updateTime(self, timestep):
        self.time += timestep
    
    def value(self):        
        base = self.money
        for key, value in self.stocksOwned.items():
            if self.market.getPrice(key, self.time) is None:
                print("Value unknown right now")
                return
            base += self.market.getPrice(key, self.time)*value
        return base

# %%
class Market:
    """
        Market is going be a csv/live data manager.  It will load relevent csvs when I try to buy, sell or query price.  It will keep csvs loaded while they are in use, and remove after

        Formally: if we ask to get price for a ticker/time pair that we haven't used before, then load the relevant csv

        intraDayDFDict should be {"Ticker": dayDFDict}
        dayDFDict should be {date: dayDF}

        ramAvailableCap - make sure there is at least _ available space in ram (number of bytes)
        
        pathToCSV will go to the output folder
    """
    def __init__(self, pathToCSV="./IEX_historical-prices/script/output/2020", ramAvailableCap=5E6,intraDayDFDict={}): # just putting intradayDF here to test, not permanent
        self.intraDayDFDict = intraDayDFDict
        self.usage = {}
        self.ramAvailableCap = ramAvailableCap
        self.pathToCSV = pathToCSV
    
    def getPrice(self, ticker, time):
        self.ensureLoaded(ticker, time)

        dateStr = datetime.strftime(time, "%Y-%m-%d")
        timeStr = datetime.strftime(time, "%H:%M")
        intraDayDF = self.intraDayDFDict[ticker][dateStr]
        # NOTE: [dateStr] is for future feature
        # print("Getting ", ticker, " at ", time)

        #TODO: better handle when that minute isn't available
        filteredRow = intraDayDF.loc[(intraDayDF["date"] == dateStr) & (intraDayDF["minute"] == timeStr)]
        if len(filteredRow) != 0 and not np.isnan(filteredRow.iloc[0]['average']):
            return filteredRow.iloc[0]['average']
        else:
            return None

    def ensureLoaded(self, ticker, time):
        """
            Maintain cache to make sure data frame is available and read from csv
        """
        dateStr = datetime.strftime(time, "%Y-%m-%d")
        
        if self.intraDayDFDict.get(ticker, True):
            self.intraDayDFDict[ticker] = {}
        if self.intraDayDFDict[ticker].get(dateStr, True):
            # check if need to evict a DF to make space for new DF
            dateStr2 = datetime.strftime(time, "%Y%m%d")
            weekNum = "{0:02d}".format(time.isocalendar()[1])
            file_path = self.pathToCSV + "/"
            file_path += datetime.strftime(time, "%Y") + "-CW" 
            file_path += weekNum + "/"
            file_path += dateStr2 + "/DONE/" 
            file_path += dateStr2 + "_" + ticker + ".csv"
            wantedSize = os.path.getsize(file_path)

            # Evict files until you have enough space for the new file
            while int(psutil.virtual_memory()[1]) - 1.1 * wantedSize < self.ramAvailableCap:
                # remove the least used date dataframe
                skey, sval = list(self.usage.items())[0]

                for key, val in self.usage.items():
                    if val < sval:
                        sval = val
                        skey = key

                self.usage.pop(skey)
                self.intraDayDFDict[skey[0]].pop(skey[1], None)
            
            # add load csv into data frame
            dateDF = pd.read_csv(file_path)
            self.intraDayDFDict[ticker][dateStr] = dateDF
            self.usage[(ticker, dateStr)] = datetime.now()
                        
# %%
AAPLDayDict = {"2020-02-24": idf2}
testMarket = Market(None, intraDayDFDict = {"AAPL": AAPLDayDict})
print(testMarket.getPrice("AAPL", datetime.strptime("2020-02-24 09:56", "%Y-%m-%d %H:%M")))

# %%
# time = datetime.strptime("09:30", "%H:%M")
# idf2.loc[idf2["date"]=="2020-02-24"]
# idf2["minute"] = idf2["minute"].apply(lambda x: datetime.strptime(x, "%H:%M"))
# %%
idf2.loc[(idf2["date"] == "2020-02-24") & (idf2["minute"] == "09:56")].average

#%%
print(psutil.virtual_memory())  # physical memory usage
print('memory % used:', psutil.virtual_memory()[2])

# %%
ticker = "LYFT"
pathToCSV = "./IEX_historical-prices/script/output/2020"
time = datetime.strptime("2020-02-24", "%Y-%m-%d")
dateStr = datetime.strftime(time, "%Y%m%d")
weekNum = "{0:02d}".format(time.isocalendar()[1])
file_path = pathToCSV + "/" + datetime.strftime(time, "%Y") + "-CW" + weekNum + "/" + dateStr + "/DONE/" + dateStr + "_" + ticker + ".csv"

print(os.path.getsize(file_path))

# %%
