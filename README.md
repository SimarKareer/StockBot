# StonkBot
Ez stonks aquire currency

## Setup
First make an account on https://iexcloud.io

Then make an empty config.json in the base folder AND in the IEX_historical-prices/script folder. Take your secret API token and put it into the file to look like this...
```
{
    "TOKEN": "sk_84a41298ed784f75bf6d15853fb489f0"
}
```

Then go run ``IEX_historical-prices/script/download_IEX.py``.  Go into the generated output folder and unzip any folders with data you want to use.  Then you can go run main.py.
