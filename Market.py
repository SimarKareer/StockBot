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