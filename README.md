# StonkBot
Ez stonks aquire currency

## Setup
First make an empty config.json in the base folder and in the IEX_historical-prices folder.  Make that file look like this...
```
{
    "TOKEN": "sk_84a41298ed784f75bf6d15853fb489f0"
}
```

Then go run ``IEX_historical-prices/script/download_IEX.py``.  Go into the generated output folder and unzip any folders with data you want to use.  Then you can go run main.py.
