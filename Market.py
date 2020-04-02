from datetime import datetime, time, timedelta
import pandas as pd
import os
import numpy as np
import heapq
import psutil
from DFInfo import DFInfo

class Market:
    """
        Market is a CSVs and (to be ) live data manager.  It loads and unloads CSVs as needed

        intraDayDFDict shoulda be {"Ticker": dayDFDict}
        dayDFDict should be {date: dayDF}
        
        pathToCSV will go to the output folder
    """
    def __init__(self, openTrade=time(hour=9, minute=30, second=00), closeTrade=time(hour=16, minute=0, second=00), pathToCSV="./IEX_historical-prices/script/output/2020", ramAvailableCap=5E6,intraDayDFDict={}):
        """
            Initialization method for Market

            Args:
                openTrade (datetime.time): Time at which the market opens trading
                closeTrade (datetime.time): Time at which the market closes trading
                pathToCSV (string) Path relative to this file for the 2020 folder in IEX_historical-prices
                ramAvailableCap (int): Computer must have ramAvailableCap bytes left when loading CSVS
                intraDayDfDict (dictionary): Dictionary of form {"Ticker": dayDFDict} dayDFDict should be {date: dayDF}
                lastIndex (int): last row we read in 
            Returns:
                None
        """
        self.intraDayDFDict = intraDayDFDict
        self.usage = {}
        self.ramAvailableCap = ramAvailableCap
        self.pathToCSV = pathToCSV
        self.openTrade = openTrade
        self.closeTrade = closeTrade
        self.timerTotal = timedelta(hours = 0)

        self.pdTimerTotal = timedelta(hours=0)
    
    def getCSVPrice(self, ticker, time):
        """
            Gets the price of a given ticker at a given time

            Args:
                ticker (String): What the variable name says my guy
                time (String): ya know, the time
            
            Returns:
                np.float: The associated price
        """
        # self.__ensureLoaded(ticker, time)
        self.__ensureLoadedWrapper(ticker, time)

        dateStr = datetime.strftime(time, "%Y-%m-%d")
        # timeStr = datetime.strftime(time, "%H:%M")
        intraDayDFInfo = self.intraDayDFDict[ticker][dateStr]
        filteredRow = intraDayDFInfo.access(time)
            
        # NOTE: [dateStr] is for future feature
        # print("Getting ", ticker, " at ", time)

        #TODO: better handle when that minute isn't available)
        if (filteredRow is not None) and (not np.isnan(filteredRow['average'])):
            if filteredRow["date"] != dateStr:
                raise ValueError("Date does not match expected date")
            return filteredRow['average']
        else:
            return None

    def getAPIPrice(self, ticker, time):
        """
            Gets price of ticker using API call

            Args:
                ticker (String): What the variable name says my guy
                time (String): ya know, the time

            Returns:
                (np.float) associated price
        """
        pass

    def __ensureLoadedWrapper(self, ticker, time):
        start = datetime.now()
        self.__ensureLoaded(ticker, time)
        end = datetime.now()
        self.timerTotal += end-start


    def __ensureLoaded(self, ticker, time):
        """
            Given a ticker and time, it will ensure the relevant CSV is loaded.  This method has a simple CSV caching system.  It keeps CSVs which are used often in memory, and releases those that are least used.  
        """
        dateStr = datetime.strftime(time, "%Y-%m-%d")
        
        if not self.intraDayDFDict.get(ticker, False):
            self.intraDayDFDict[ticker] = {}
        if not self.intraDayDFDict[ticker].get(dateStr, False):
            # check if need to evict a DF to make space for new DF
            dateStr2 = datetime.strftime(time, "%Y%m%d")
            weekNum = "{0:02d}".format(time.isocalendar()[1])
            file_path = self.pathToCSV + "/" + datetime.strftime(time, "%Y") + "-CW" + weekNum
            file_path += "/" + dateStr2 + "/DONE/" + dateStr2 + "_" + ticker + ".csv"
            wantedSize = os.path.getsize(file_path)

            printedError = False
            # Evict files until you have enough space for the new file
            while int(psutil.virtual_memory()[1]) - 1.1 * wantedSize < self.ramAvailableCap:
                # remove the least used date dataframe
                try:
                    skey, sval = list(self.usage.items())[0]

                    for key, val in self.usage.items():
                        if val < sval:
                            sval = val
                            skey = key

                    self.usage.pop(skey)
                    self.intraDayDFDict[skey[0]].pop(skey[1], None)
                except IndexError:
                    if not printedError:
                        print("Over RAM cap but no CSV files loaded, waiting for garbage collector...")
                        printedError = True
                   
            print('loading', file_path)
            start = datetime.now()
            # add load csv into data frame
            dateDF = pd.read_csv(file_path)
            end = datetime.now()
            self.pdTimerTotal += end-start

            # This is the initialization for this DF, which is why lastIndex is set to -1
            self.intraDayDFDict[ticker][dateStr] = DFInfo(dateDF)
            self.usage[(ticker, dateStr)] = datetime.now()