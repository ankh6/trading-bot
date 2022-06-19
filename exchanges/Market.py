from abc import ABCMeta
from typing import List, Tuple
from Constants import BASE_URL, API_VERSION
from requests import get


class Exchange(metaclass=ABCMeta):
    def __init__(self):
        self.symbol = None
        self.base_asset : str = None
        self.quote_asset : str = None
        self._timeout : int = None
        self._rate_limit_time : str = None
        self._rate_limit : int = None

    def fetch_exchange_given_trading_pairs(self, url: str, version: str, endpoint: str, params: List[Tuple[str,str]]):
        request_parameters = params
        full_path = url+ version + "/" + endpoint
        response = get(url=full_path, params=request_parameters)
        return response.json()
    
    def initialize(self, trading_pair : str):
        ''' Initializes the Exchange object with its properties
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

    def fetch_price_data_given_symbol(self, time: str, interval_type:str):
        _interval = time + interval_type
        exchange_info = self.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="klines",params=[("symbol", self.symbol),("interval", _interval)])
        # TO-DO
        # No need to define types of interval because data will be fetched once the script runs (e.g. every 5 minute)
        # Convert binance array to numpy array
        # Create pandas dataframe for data manipulations
        # Name of columns depend on data we fetch