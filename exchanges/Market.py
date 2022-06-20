from abc import ABCMeta
from typing import List, Tuple
from Constants import BASE_URL, API_VERSION
from requests import get
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

    def fetch_price_data_given_symbol(self, time: str, interval_type:str):
        ''' Fetches the symbol trading attributes from Binance API

        Arguments:
        time: an integer from 1 to 9
        interval_type: case-sensitive, s(SECOND), m(MINUTE), h(HOUR), d(DAY)
        See their documentation for the enums they support: https://binance-docs.github.io/apidocs/spot/en/#limits

        Returns:
        exchange_info: a numpy array that stores the trading attributes
        '''
        _interval = time + interval_type
        exchange_info = self.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="klines",params=[("symbol", self.symbol),("interval", _interval)])
        return np.array(exchange_info,copy=False)
        
