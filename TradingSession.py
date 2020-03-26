class TradingSession:
    """
        A trading session keeps track of all the stocks and portfolios you've bought, and at what price you bought them.
        Keeps track of current time, and won't allow you to access any data beyond your current time.
    """
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