from abc import ABCMeta
from time import sleep, time
from Constants import API_VERSION, BASE_URL, BOT_RUNNING_FREQUENCY_IN_SECONDS, CROSSING_POINT, INTERVAL_TIME, RSI_OVERSOLD_LIMIT, RSI_OVERBOUGHT_BOUND
from orders.Order import OrderType, Side
from services import Reporter, Web
from strategies import MomentumStrategy
from utils import ExchangeHelper
import sched
import numpy as np
import pandas as pd


class Exchange(metaclass=ABCMeta):
    def __init__(self):
        self.symbol: str = None
        self.base_asset : str = None
        self.quote_asset : str = None
        self._trend_direction : int = None
        self.date = None
        self.open_price: int = None
        self.close_price: int = None
    
    def initialize(self, trading_pair : str):
        ''' Initializes the Exchange object with its properties

        Arguments:
        trading_pair: A string without a "/" separating the base asset from the quote, e.g. ETH/USDC -> ETHUDSC
        '''
        exchange_info = Web.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="exchangeInfo" ,params=[("symbol", trading_pair)])
        symbols = exchange_info["symbols"]
        self.symbol = trading_pair
        self._symbols = symbols[0]["symbol"]
        self.base_asset = symbols[0]["baseAsset"]
        self.quote_asset = symbols[0]["quoteAsset"]
    
    def fetch_price_data_given_symbol(self) -> np.array:
        ''' Fetches the symbol trading attributes from Binance API

        Returns:
        exchange_info: a numpy array that stores the trading attributes
        '''
        _interval = INTERVAL_TIME
        exchange_info = Web.fetch_exchange_given_trading_pairs(url=BASE_URL, version=API_VERSION, endpoint="klines",params=[("symbol", self.symbol),("interval", _interval)])
        return np.array(exchange_info, copy=False)
            
    def get_most_recent_date(self, trading_attribute_dataframe: pd.DataFrame):
        ''' Retrieves the last date

        Arguments:
        trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

        Returns:
        the date
        '''
        dates = trading_attribute_dataframe.loc[:,"Close time"]
        return dates.loc[dates.size - 1]
    
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
        ExchangeHelper.convert_object_series_to_datetime(df, ["Open time", "Close time"])
        return df
    
    def get_closing_price(self, trading_attributes_dataframe: pd.DataFrame) -> int:
        '''
        Arguments:
        trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset
        
        Returns:
        The most recent closing price

        '''
        closing_price_series = trading_attributes_dataframe.loc[:, "Close"]
        self.close_price = closing_price_series.loc[closing_price_series.size - 1]
        return self.close_price

    def get_opening_price(self, trading_attributes_dataframe: pd.DataFrame):
        '''
        Arguments:
        trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset

        Returns:
        The most recent opening price

        '''
        opening_price_series = trading_attributes_dataframe.loc[:, "Open"]
        self.open_price = opening_price_series.loc[opening_price_series.size - 1]
        return self.open_price
    
    # TO-DO
    # Implement logic to use a fraction of the user's quantity
    def set_asset_quantity(self, quantity: int):
        return quantity

    
    def execute_strategy(self, trading_attributes_dataframe: pd.DataFrame, rsi: int) -> OrderType:
        ''' Executes the trading strategy depending on the values of the technical indicators, EMA and RSI

        Arguments:
        trading_attributes_dataframe: the source dataframe that stores the closing prices of the base asset
        rsi: The Relative Strength Index for the time period 
        Returns:
        The side of the action, a buy, a sell or neutral
        '''
        open_price = self.get_opening_price(trading_attributes_dataframe)
        close_price = self.get_closing_price(trading_attributes_dataframe)
        try:
            self._trend_direction = MomentumStrategy.find_trend_direction(trading_attributes_dataframe)
            # CROSSING_POINT equals 0.0, i.e. EMA long-term = EMA short-term or EMA short-term - EMA long-term = 0
            # Upward direction of the trend
            if ((close_price > open_price) or (self._trend_direction > CROSSING_POINT)) and (rsi < RSI_OVERSOLD_LIMIT):
                # Default value
                # Example
                quantity = self.set_asset_quantity(0)
                print(f"Very strong buy signals: {close_price}, {open_price}\n{rsi}")
                Web._create_new_order(self.symbol, Side.BUY, OrderType.MARKET_ORDER, quote_quantity=quantity)
                return Side.BUY
            
            elif rsi < RSI_OVERSOLD_LIMIT or ((close_price > open_price) and (self._trend_direction > CROSSING_POINT)):
                quantity = self.set_asset_quantity(0)
                print(f"Strong buy signals: {close_price}, {open_price}\n{rsi}")
                Web._create_new_order(self.symbol, Side.BUY, OrderType.MARKET_ORDER, quote_quantity=0)
                return Side.BUY
            
            # Downard direction of the trend
            elif ((open_price > close_price) or (self._trend_direction < CROSSING_POINT)) and (rsi > RSI_OVERBOUGHT_BOUND):
                quantity = self.set_asset_quantity(0)
                print(f"Very strong sell signals: {open_price}, {close_price}\n{rsi}")
                Web._create_new_order(self.symbol, Side.SELL, OrderType.MARKET_ORDER, quote_quantity=0)
                return Side.SELL
            
            elif rsi > RSI_OVERBOUGHT_BOUND or ((open_price > close_price ) and (self._trend_direction < CROSSING_POINT)):
                quantity = self.set_asset_quantity(0)
                print(f"Strong sell signals: {open_price}, {close_price}\n{rsi}")
                Web._create_new_order(self.symbol, Side.SELL, OrderType.MARKET_ORDER, quote_quantity=0)
                return Side.SELL
            # Buy or strong signals were not strong enough
            # do nothing
            else:
                print("Buy or Sell signals were not strong enough!\nKeep position")
                return Side.NEUTRAL
        except IndexError:
            print("There were no crossing observed")
        except Exception as e:
            print(e.args)
            raise e

    
    def run(self):
        '''
        Main routine
        '''
        self.initialize("ETHUSDC")
        print("Fetching data from Binance API . . . ")
        trading_attributes = self.fetch_price_data_given_symbol()
        df_trading_attributes = self.create_symbol_dataframe(symbol_trading_attributes=trading_attributes)
        self.date = self.get_most_recent_date(df_trading_attributes)
        print(f"Last observation on {self.date}")
        print("Computing RSI, short-/long-term EMAs to make a decision ... ")
        short_ema, long_ema = MomentumStrategy.find_latest_short_long_ema(trading_attributes_dataframe=df_trading_attributes)
        rsi = MomentumStrategy.compute_rsi(trading_attributes_dataframe=df_trading_attributes)
        side = self.execute_strategy(df_trading_attributes, rsi)
        print("Building report . . . ")
        Reporter._create_trading_report(date=self.date, symbol=self.symbol, short_ema=short_ema, long_ema=long_ema, rsi=rsi, side=side)
        print("Report done !")
        # Executes the trading strategy every 5 minutes
        # priority, mandatory argument. 1 equals the highest priority
        scheduler.enter(delay=BOT_RUNNING_FREQUENCY_IN_SECONDS, priority=1, action=self.run)
        scheduler.run()



if __name__ == '__main__':
    try:
        scheduler = sched.scheduler(time,sleep)
        exchange = Exchange()
        exchange.run()
    except Exception as e:
        print(e.args)
        raise e

