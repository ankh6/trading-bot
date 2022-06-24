from exchanges.Constants import EMA_SHORT_TERM, EMA_LONG_TERM
from talib import EMA, RSI
from typing import Tuple
import pandas as pd

def compute_short_long_ema(trading_attributes_dataframe: pd.DataFrame) -> Tuple[int,int] :
    ''' Computes the Exponential Moving Average on the close prices for both short and long timeperiods

    timeperiod argument (EMA function) is the number of observations required to compute the first EMA value
    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

    Returns:
    ema_short_term: The short-term EMA pandas Series
    ema_long_term: The long-term EMA pandas Series
    '''
    close_prices_series = trading_attributes_dataframe.loc[:, "Close"]
    ema_short_term = EMA(close_prices_series, timeperiod=EMA_SHORT_TERM)
    ema_long_term = EMA(close_prices_series, timeperiod=EMA_LONG_TERM)
    return (ema_short_term, ema_long_term)


def find_latest_short_long_ema(trading_attributes_dataframe: pd.DataFrame):
    ''' Computes the EMA values for short and long-term periods

    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

    Returns:
    latest_short_term_ema: The short-term EMA for the last observation givne the short timeperiod, i.e. 12 observations
    latest_long_term_ema: The long-term EMA for the last observation given the long timeperiod, i.e. 26 observations

    '''
    ema_short_term, ema_long_term = compute_short_long_ema(trading_attributes_dataframe)
    latest_short_term_ema  = ema_short_term.loc[ema_short_term.size - 1]
    latest_long_term_ema = ema_long_term.loc[ema_long_term.size - 1]
    return (latest_short_term_ema, latest_long_term_ema)

def find_trend_direction(trading_attributes_dataframe: pd.DataFrame):
    ''' Helper method to find the direction of the trend

    This functions relies on calculation the pandas Series that is the difference between the short and long-term EMA

    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset
    
    Returns:
    An signed integer that is the difference between the short and long-term EMA at the last observation

    '''
    ema_short_term, ema_long_term = compute_short_long_ema(trading_attributes_dataframe)
    # Finds cross, i.e. a point where both EMAs have the same value
    res = ema_short_term - ema_long_term
    return res.loc[res.size - 1]

def compute_rsi(trading_attributes_dataframe: pd.DataFrame) -> int :
    ''' Computes the Relative Strength Index on the close prices
    Arguments:
    trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

    Returns:
    The RSI for the last observation given the time period
    '''
    close_prices = trading_attributes_dataframe.loc[:, "Close"]
    rsi_series = RSI(close_prices, timeperiod=EMA_LONG_TERM)
    return rsi_series.loc[close_prices.size - 1]