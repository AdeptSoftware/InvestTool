# t_interval.py
from clients.abstract.interval  import AbstractInterval
from tinkoff.invest             import CandleInterval       as _Ci
from tinkoff.invest             import SubscriptionInterval as _Si
import datetime

class TInterval(AbstractInterval):
    MIN_1       = (0,  "1M",    1,      1,     _Ci.CANDLE_INTERVAL_1_MIN,  _Si.SUBSCRIPTION_INTERVAL_ONE_MINUTE)
    MIN_2       = (1,  "2M",    2,      1,     _Ci.CANDLE_INTERVAL_2_MIN,  _Si.SUBSCRIPTION_INTERVAL_2_MIN)
    MIN_3       = (2,  "3M",    3,      1,     _Ci.CANDLE_INTERVAL_3_MIN,  _Si.SUBSCRIPTION_INTERVAL_3_MIN)
    MIN_5       = (3,  "5M",    5,      7,     _Ci.CANDLE_INTERVAL_5_MIN,  _Si.SUBSCRIPTION_INTERVAL_FIVE_MINUTES)
    MIN_10      = (4,  "10M",   10,     7,     _Ci.CANDLE_INTERVAL_10_MIN, _Si.SUBSCRIPTION_INTERVAL_10_MIN)
    MIN_15      = (5,  "15M",   15,     7,     _Ci.CANDLE_INTERVAL_15_MIN, _Si.SUBSCRIPTION_INTERVAL_FIFTEEN_MINUTES)
    MIN_30      = (6,  "30M",   30,     7,     _Ci.CANDLE_INTERVAL_30_MIN, _Si.SUBSCRIPTION_INTERVAL_30_MIN)
    HOUR_1      = (7,  "1H",    60,     7,     _Ci.CANDLE_INTERVAL_HOUR,   _Si.SUBSCRIPTION_INTERVAL_ONE_HOUR)
    HOUR_2      = (8,  "2H",    120,    30,    _Ci.CANDLE_INTERVAL_2_HOUR, _Si.SUBSCRIPTION_INTERVAL_2_HOUR)
    HOUR_4      = (9,  "4H",    240,    30,    _Ci.CANDLE_INTERVAL_4_HOUR, _Si.SUBSCRIPTION_INTERVAL_4_HOUR)
    DAY         = (10, "1D",    1440,   366*2, _Ci.CANDLE_INTERVAL_DAY,    _Si.SUBSCRIPTION_INTERVAL_ONE_DAY)
    WEEK        = (11, "7D",    10080,  366*2, _Ci.CANDLE_INTERVAL_WEEK,   _Si.SUBSCRIPTION_INTERVAL_WEEK)
    MONTH       = (12, "30D",   302400, 366*10,_Ci.CANDLE_INTERVAL_MONTH,  _Si.SUBSCRIPTION_INTERVAL_MONTH)
