from talib import EMA, RSI
from typing import Tuple
import pandas as pd

def compute_short_long_ema(trading_attributes_dataframe: pd.DataFrame, short_term_period: int=12, long_term_period: int=26) -> Tuple[int,int] :
    ''' Computes the Exponential Moving Average on the close prices for both short and long timeperiods

    timeperiod argument (EMA function) is the number of observations required to compute the first EMA value
    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

    Returns:
    latest_short_term_ema: The short-term EMA for the last observation givne the short timeperiod, i.e. 12 observations
    latest_long_term_ema: The long-term EMA for the last observation given the long timeperiod, i.e. 26 observations
    '''
    close_prices_series = trading_attributes_dataframe.loc[:, "Close"]
    ema_short_term = EMA(close_prices_series, timeperiod=short_term_period)
    ema_long_term = EMA(close_prices_series, timeperiod=long_term_period)
    latest_short_term_ema  = ema_short_term.loc[close_prices_series.size - 1]
    latest_long_term_ema = ema_long_term.loc[close_prices_series.size - 1]
    return (latest_short_term_ema, latest_long_term_ema)


def compute_rsi(trading_attributes_dataframe: pd.DataFrame,  time_period: int = 26) -> int :
    ''' Computes the Exponential Moving Average on the close prices
    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

    Returns:
    The RSI for the last observation given the time period
    '''
    close_prices = trading_attributes_dataframe.loc[:, "Close"]
    rsi_series = RSI(close_prices, timeperiod=time_period)
    return rsi_series.loc[close_prices.size - 1]