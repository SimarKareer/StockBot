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

#TODO: multiple days tests
#TODO: Live Data

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
