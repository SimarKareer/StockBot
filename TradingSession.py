from datetime import datetime, timedelta
class TradingSession:
    """
        A trading session keeps track of all the stocks and portfolios you've bought, and at what price you bought them.
        Keeps track of current time, and won't allow you to access any data beyond your current time.
    """
    def __init__(self, logLocation, money, market, time, verbosity=1):
        """
            Initialization for trading session

            Args:
                logLocation (string): location of the log file
                money (int): starting amount of money in dollars
                market (Market): The market (which holds the pricing info) on which we are trading
                time (datetime.time): The current simulated (or potentially live) time
                verbosityLevel (int): 0 - none, 1 - daily, 2 - hourly
            
            Returns:
                None
        """
        self.stocksOwned = {}
        self.logLocation = logLocation
        self.initMoney = money
        self.money = money
        self.market = market
        self.time = time
        self.verbosity = verbosity
        self.realTimeStart = datetime.now()
    
    def end(self):
        #TODO: saves output log file
        print("Finished Session with final value of $", self.value())
        print("Time in ensureLoaded: ", self.market.timerTotal)
        print("Time loading CSVs: ", self.market.pdTimerTotal)
        print("Total Time: ", datetime.now() - self.realTimeStart)

    def trade(self, ticker, quantity):
        """
            Function to buy/sell those good stonks.  If the price at this time is unknown we return without editing the state.

            Args:
                ticker (string): the stonk you want to trade
                quantity (int): number of stonks (+buy, -sell)

            Returns:
                None
        """
        # adds smaller information into log string
        #ex) AAPL, 10, $100, time
        # TODO: Add a getprice wrapper to make sure you can't see into the future
        if self.getPrice(ticker, self.time) is None:
            return

        if ticker in self.stocksOwned:
            if self.stocksOwned[ticker] + quantity < 0:
                raise ValueError("You are trying to sell stonks you don't have")
            else:
                self.stocksOwned[ticker] += quantity
        else:
            self.stocksOwned[ticker] = quantity
        #TODO: UPDATE netvalue

        # print("Bought at price: ", self.market.getPrice(ticker, self.time))
        deltaMoney = -quantity * self.getPrice(ticker, self.time)
        if self.money + deltaMoney < 0:
            raise ValueError("You are trying to use money you don't have")
        else:
            self.money -= quantity * self.getPrice(ticker, self.time)

    def getPrice(self, ticker, time):
        """
            Wrapper function for getting price in a way that we have access to the current time.

            Args:
                ticker (string): the stonk we want
                time (datetime.datetime): at what time
            
            Returns:
                (np.float) price if available or (None) if not
        """
        if time > self.time:
            raise ValueError("Trying to access time beyond current time")
        elif time.date == datetime.now().day:
            return self.market.getAPIPrice(ticker, time)
        else:
            return self.market.getCSVPrice(ticker, time)
    
    def updateTime(self, timestep):
        """
            Update simulation time with respect to the open and close times of the provided Market

            Args:
                timestep (datetime.timedelta): Difference in time
            
            Returns:
                None
        """
        #TODO: There appears to be an off by 1 error here
        if (self.time + timestep).time() > self.market.closeTrade:
            self.time = datetime.combine(self.time.date() + timedelta(days = 1), self.market.openTrade)
        else:
            if self.verbosity >= 1 and ((self.time + timestep).time() == self.market.closeTrade):
                print("At t=", self.time, " our total value is ", self.value())
            if self.time.minute == 0 and self.verbosity >= 2:
                print("At t=", self.time, " our total value is ", self.value())
            self.time += timestep

    def value(self):     
        """
            Calculates value of current portfolio + cash available

            Args: None

            Returns:
                (int) our net value
        """   
        base = self.money
        for key, value in self.stocksOwned.items():
            if self.getPrice(key, self.time) is None:
                print("Value unknown right now")
                return
            base += self.getPrice(key, self.time)*value
        return base