# trading-bot

## Getting started

**You will need to have the latest version of [Python](https://www.python.org/downloads/) and [Visual Studio Code](https://code.visualstudio.com/download) installed !**

If you would still like to run the bot from source please follow the instructions below 👇

### Clone the repo
'''
git clone https://github.com/ankh6/trading-bot.git
'''

### Install the requirements
'''
pip install -r requirements.txt 
'''


### Add your API-KEY and SIGNATURE as environment variables
This step is **mandatory** to make orders.

### Open your favorite terminal 
### Navigate to the trading-bot

'''
cd path/to/exchanges/folder
'''

### Run the trading-bot
'''
python Market.py
'''

## Features

Centralized exchange(s) supported : Binance

Depending on the trading pair you are interested in, the trading bot initializes itself by retrieving the exchange for the given exchange (e.g. ETHUSDC). It does so by hitting the '''exchangeInfo''' [Binance endpoint](https://binance-docs.github.io/apidocs/spot/en/#exchange-information). We do not store every data provided by response payload. In fact, we only need the symbol (ETHUSDC), the base asset (ETH) and the quote asset (USDC)

Once the Exchange properties are set, the bot retrieves the market data point by hitting the '''klines''' [Binance endpoint](https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data). The response payload exposes order books's information and data points that any trader/quant is familiar with:
- Open time
- Open price
- Open
- High
- Low
- Close
- Volume
- Close time
- Quote asset volume
- Number of trades
- Taker buy base-/quote asset volume

The interval for the data market point is **1 day**

We store these data point in an array that will serve as an argument to create our dataframe. We transform some of the features before having a final dataframe. Features are
- Dropping the ignore data point, provided by Binance
- Converting 'Open time' and 'Close time' of type unix epoch time (ms) to a pandas datetime object


The bot relies on a Momentum strategy to decide going long or short on a position. The bot uses the [talib](https://github.com/mrjbq7/ta-lib/blob/master/README.md) library to compute the Exponential Moving Average and the Relative Strength Index. The former gives the direction of the trend while the latter gives the strength of the trend. We compute two EMA that have different time periods: the short-term EMA (SEMA) for 12 days and the long-term EMA (LEMA) for 26 days. We determine the sign of the EMA by calculating the difference between the LEMA and SEMA:
- positive sign -> SEMA > LEMA -> upward trend
- negative sign -> LEMA > SEMA -> downward trend

N.B. For more detailed information on technical indicators, please visit [EMA](http://www.tadoc.org/indicator/EMA.htm), [RSI](http://www.tadoc.org/indicator/RSI.htm)

Alongside the indicators, the trading bot takes into account the closing price against the opening price to determine if market conditions are bullish or bearish. The strategy is fairly simple: the trading bot computes both technical indicators, verifies the market sentiment and acts accordingly:
1. Very strong bullish signal:
- close price > open price **OR** EMA is positive **AND**
- RSI is below 20, the asset is **oversold**

2. Strong bullish signal:
- RSI is below 20, the asset is **oversold**, **OR**
- close price > open price **AND** EMA is positive

3. Very strong bearish signal:
- open price > close price **OR** EMA is negative, **AND**
-  RSI is above 80, the asset is **overbought**

4. Strong bearish signal:
- RSI is above 80, the asset is **overbought¨**, **OR**,
- open price > close price **AND** EMA is negative

5. Neither buy or sell signal were strong enough -> do nothing


Once the trading bot has taken a decision and the new order has gone through, a *trading report* file is created. This file summarizes the date, the trading pair, the value of SEMA, the value of LEMA, the rsi and the side of the transaction.

If you do not interrupt it (open the terminal, ''' CTRL+C'''), the trading bot runs **every day** forever

## What is next ?
- Read coins from user
- Integrate asset

## Disclaimer
This software is for educational purposes only. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Do not risk money which you are afraid to lose. There might be bugs in the code - this software DOES NOT come with ANY warranty.