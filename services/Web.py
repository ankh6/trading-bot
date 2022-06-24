from typing import List, Optional, Tuple
from orders.Order import OrderType, Side
from requests import get, post

def fetch_exchange_given_trading_pairs(url: str, version: str, endpoint: str, params: List[Tuple[str,str]]):
    ''' Helper function to fetch data given a url, endpoint and request parameters (optional)
    
    Arguments:
    url: string, the base URI (Uniform Resource Identifier)
    version: version of the Binance API
    endpoint: a string, the endpoint
    params: list of tuples, the request parameters (optional)
        
    Return:
    response, the resources in a json format
    '''
    request_parameters = params
    full_path = url+ version + "/" + endpoint
    response = get(url=full_path, params=request_parameters)
    return response.json()

# TO-DO
# Implement reading account of the user
# Know how much user has of base and quote assets
# Integrate asset quantity
# Sell-side : Not sell more than user has
def _create_new_order(symbol: str, side: Side, type: OrderType, asset_quantity: Optional[int]):
    ''' Sends a POST request to Binance
    Arguments:
    symbol: the trading pair
    side: the side of the order, buy or sell
    type: the type of the order. Only Market order
    asset_quantity: the quantity of the asset to either buy or sell
    '''
    request_parameters = [("symbol", symbol), ("side", side), ("type", type), ("Content-Type", "application/x-www-form-urlencoded"), ("X-MBX-APIKEY", API_KEY), ("signature", SIGNATURE)]
    if side.BUY:
        param = ("quantity", asset_quantity)
        request_parameters.append(param)
    full_path = BASE_URL + API_VERSION + "/" + "order"
    post(full_path, data=request_parameters)
