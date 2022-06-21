from abc import ABCMeta
from typing import List, Optional, Tuple
from Constants import BASE_URL, API_VERSION
from strategies import MomentumStrategy
from orders.Order import OrderType, Side
from errors.Exceptions import LabelNotFoundError
from requests import get, post
from time import sleep, time
import sched
import numpy as np
import pandas as pd


class Exchange(metaclass=ABCMeta):
    def __init__(self):
        self.symbol = None
        self.base_asset : str = None
        self.quote_asset : str = None
        self._timeout : int = None
        self._rate_limit_time : str = None
        self._rate_limit : int = None

    def fetch_exchange_given_trading_pairs(self, url: str, version: str, endpoint: str, params: List[Tuple[str,str]]):
        ''' Helper function to fetch data given a url, endpoint and request parameters (optional)

        Arguments:
        url: string, the base URI (Uniform Resource Identifier)
        endpoint: a string, the endpoint
        params: list of tuples, the request parameters (optional)
        
        Return:
        response, the resources in a json format
        '''
        request_parameters = params
        full_path = url+ version + "/" + endpoint
        response = get(url=full_path, params=request_parameters)
        return response.json()
    
    def initialize(self, trading_pair : str):
        ''' Initializes the Exchange object with its properties

        Arguments:
        trading_pair: A string without a "/" separating the base asset from the quote, e.g. ETH/USDC -> ETHUDSC
        '''
        exchange_info = self.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="exchangeInfo" ,params=[("symbol", trading_pair)])
        rate_limit = exchange_info["rateLimits"]    
        symbols = exchange_info["symbols"]
        self.symbol = trading_pair
        self._rate_limit_time = rate_limit[-1]["interval"]
        self._rate_limit = rate_limit[-1]["limit"]
        self._symbols = symbols[0]["symbol"]
        self.base_asset = symbols[0]["baseAsset"]
        self.quote_asset = symbols[0]["quoteAsset"]
    
    def fetch_price_data_given_symbol(self) -> np.array:
        ''' Fetches the symbol trading attributes from Binance API

        Returns:
        exchange_info: a numpy array that stores the trading attributes
        '''
        _interval = "5m"
        exchange_info = self.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="klines",params=[("symbol", self.symbol),("interval", _interval)])
        return np.array(exchange_info, copy=False)
        
    
    def convert_object_to_string(self, input) -> object:
        ''' Converts an input of type object to an input of type string

        Arguments:
        input, the input to be converted

        Return:
        input: the converted input
        '''
        return str(input)

    def convert_object_series_to_datetime(self, source_dataframe: pd.DataFrame, timestamp_labels: List[str]):
        ''' Converts a pandas series of unix epoch milliseconds (timestamps) values into a series of datetime values
        
        By the default the function updates inplace the original DataFrame
        This function facilitates the handling of time-series values
        Arguments:
        source_dataframe: the pandas DataFrame that exposes the labels to be converted
        timestamp_labels: a list of label/column names 
        '''
        print(f"Converting labels: {timestamp_labels}")
        for single_label in timestamp_labels:
            try:
                source_dataframe[single_label].apply(self.convert_object_to_string, convert_dtype=False)
                source_dataframe[single_label] = pd.to_datetime(source_dataframe[single_label], dayfirst=False, yearfirst=True, unit="ms", origin="unix", utc=True)
            except KeyError:
                raise LabelNotFoundError(f"Please provide a label that is expose by the dataframe\nProvided labels: {timestamp_labels}")
            except Exception as e:
                print(e.args)
                raise Exception
    
    
    def create_symbol_dataframe(self, symbol_trading_attributes: np.array):
        ''' Generates a DataFrame that stores attributes of a the trading pair

        Arguments:
        symbol_trading_attributes: a list of attributes that are available on the exchange for the given pair
        '''
        df = pd.DataFrame(data=symbol_trading_attributes, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volumes", "Number of trades", "Taker buy base volume", "Take buy quote volume", "Ignore"])
        # Binance stores a value at the last index of each set of observations
        # Per documentation, this value is set as "Ignored"
        # We drop the column that stores these values
        df.drop(labels=["Ignore"], axis = 1, inplace=True)
        self.convert_object_series_to_datetime(df, ["Open time", "Close time"])
        return df


    # PAY attention to sell only what you have
    # Need user account
    # Need access to the amout of base and quote assets
    def create_new_order(self,symbol: str, side: Side, type: OrderType, quote_quantity: Optional[int]):
        request_parameters = [("symbol", symbol), ("side", side), ("type", type)]
        if side.BUY:
            param = ("quantity", quote_quantity)
            request_parameters.append(param)
        full_path = BASE_URL + API_VERSION + "/" + "order"
        post(full_path, data=request_parameters)
    

    def execute_strategy(self):
        '''
        Main routine
        '''
        self.initialize("ETHUSDC")
        print("Fetching data from Binance API . . .")
        trading_attributes = self.fetch_price_data_given_symbol()
        df_trading_attributes = self.create_symbol_dataframe(symbol_trading_attributes=trading_attributes)
        print(f"Trading attributes DataFrame: {df_trading_attributes}")
        short_ema, long_ema = MomentumStrategy.compute_short_long_ema(trading_attributes_dataframe=df_trading_attributes)
        print(f"Values of short and long ema, respectively: {short_ema} {long_ema}")
        rsi = MomentumStrategy.compute_rsi(trading_attributes_dataframe=df_trading_attributes)
        print(f"Value of RSI: {rsi}")
        # TO-DO : implements buy and sell conditions
        # upward trend when short was below long, then short crosses long
        # downward trend when long was above short, then long crosses short
        # crossing means both have the same value or short = term or short - term = 0
        # add the logic that stores both values and track equality between both values
        # take into account RSI value (RSI < 20 -> OVERSOLD -> Buy signal, RSI > 80 -> OVERBOUGHT -> Sell signal)

        # TO-DO: add reporting
        # once the job has run, store values of interest
        # date, trading_pair, value of indicators, type of order (eg BUY or SELL), order status (completed or rejected)


if __name__ == '__main__':
    try:
        scheduler = sched.scheduler(time,sleep)
        exchange = Exchange()
        # Executes the trading strategy every 5 minutes
        # priority, mandatory argument. 1 equals the highest priority
        scheduler.enter(delay=60*5, priority=1, action=exchange.execute_strategy)
    except Exception as e:
        print(e.args)
        raise Exception

