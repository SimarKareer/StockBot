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

    def buy(self, ticker, quantity):
        """
            Function to get those good stonks.  If the price at this time is unknown we return without editing the state.

            Args:
                ticker (string): the stonk you want
                quantity (int): number of stonks

            Returns:
                None
        """
        # adds smaller information into log string
        #ex) AAPL, 10, $100, time
        # TODO: Add a getprice wrapper to make sure you can't see into the future
        if self.market.getPrice(ticker, self.time) is None:
            return

        if ticker in self.stocksOwned:
            self.stocksOwned[ticker] += quantity
        else:
            self.stocksOwned[ticker] = quantity
        #TODO: UPDATE netvalue

        # print("Bought at price: ", self.market.getPrice(ticker, self.time))
        self.money -= quantity * self.market.getPrice(ticker, self.time)
    
    def sell(self, ticker, quantity):
        """
            Function to get that good profit.  If the price at this time is unknown we return without editing the state.

            Args:
                ticker (string): the stonk you want
                quantity (int): number of stonks
            
            Returns:
                None
        """
        if self.market.getPrice(ticker, self.time) is None:
            return
        self.stocksOwned[ticker] -= quantity
        self.money += quantity * self.market.getPrice(ticker, self.time)
    
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
            if self.market.getPrice(key, self.time) is None:
                print("Value unknown right now")
                return
            base += self.market.getPrice(key, self.time)*value
        return base