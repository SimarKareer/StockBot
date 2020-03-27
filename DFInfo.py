from datetime import datetime

class DFInfo:
    """
        DFInfo keeps track of a specific day/ticker dataframe.  This is needed so we can keep track of where in a dataframe we are so that we don't search the whole thing every time.
    """
    def __init__(self, df):
        """
            Initialization method
            
            Args:
                df (pd.df): dataframe for a specific ticker/day (should have uniform time between rows)
                lastIndex: the index of the last access for this dataframe
                lastTime: the last time we tried accessing (for reference)
        """
        #NOTE: we can check whether a CSV has all the values we want by doing endTime-startTime/timeDelta
        self.df = df
        startTime = datetime.strptime(df.iloc[0]["minute"] + ":" + df.iloc[0]["date"], "%H:%M:%Y-%m-%d")
        secondTime = datetime.strptime(df.iloc[1]["minute"] + ":" + df.iloc[1]["date"], "%H:%M:%Y-%m-%d")
        self.endTime = datetime.strptime(df.iloc[-1]["minute"] + ":" + df.iloc[-1]["date"], "%H:%M:%Y-%m-%d")
        
        self.startTime = startTime
        self.timedelta = secondTime - startTime

    def access(self, time):
        """
            Method to get row from dateDF

            Args:
                time: datetime object of desired access time

            Return:
                row of dateDF
        """
        if time > self.endTime:
            return None
        
        index = (time - self.startTime) / self.timedelta
        filteredRow = None

        if index == int(index):
            filteredRow = self.df.iloc[int(index)]
        
        timeStr = datetime.strftime(time, "%H:%M")
        if (filteredRow is None) or filteredRow["minute"] != timeStr:
            filteredRow = self.df.loc[self.df["minute"] == timeStr].iloc[0]
            # print('forced linear search')

        return filteredRow