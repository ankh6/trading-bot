from enum import Enum
class Side(Enum):
    BUY = 1
    SELL = 2
    NEUTRAL = 3

class OrderType(Enum):
    MARKET_ORDER = 1