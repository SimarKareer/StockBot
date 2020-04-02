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
from Market import Market
from TradingSession import TradingSession

#TODO: What to do with missing data?
#TODO: Fix CSVs live
#TODO: failsafe to make sure we can't get a price after our current date
#TODO: Live Data

# %%
def decisionLoop(tradingSession):
    """
        This decision loop is an example of a trading strategy.  The strategy gets all its decision making information from the tradingSession object
        
        Args:
            tradingSession (TradingSession): Your current trading session
        
        Returns:
            None
    """
    # print("Currently have $", tradingSession.money, "in cash")

    tradingSession.trade("LYFT", 2)
    tradingSession.trade("MSFT", 2)
    tradingSession.trade("DBX", 2)
    tradingSession.trade("AMZN", 2)
    tradingSession.trade("LYFT", -1)
    tradingSession.trade("MSFT", -1)
    tradingSession.trade("DBX", -1)
    tradingSession.trade("AMZN", -1)
    print("Net value at ", tradingSession.time, " is ", tradingSession.value())
    print("--------------------")

# %%
def runDecisionLoop(start, end, timestep, decisionLoop):
    """
        given a time period, start to end, run the algorithm implemented in decision loop for each provided timestep
        Args:
            start (datetime): time to start testing strategy
            end (datetime): time to end testing strategy
            timestep (timedelta): time between each iteration
            decisionLoop (function(tradingSession)): function defining strategy
        
        Returns:
            None
    """
    market = Market()
    ts = TradingSession(None, 100, market, start)
    print("starting with", ts.money)
    while ts.time < end:
        decisionLoop(ts)
        ts.updateTime(timestep)
    ts.end()

start = datetime.strptime("2020-02-24 9:30", "%Y-%m-%d %H:%M")
end = datetime.strptime("2020-02-26 15:59", "%Y-%m-%d %H:%M")
# end = start + timedelta(days = 3)

runDecisionLoop(start, end, timedelta(minutes = 1), decisionLoop)
# %%

