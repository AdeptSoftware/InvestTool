# storage.py                                                                                                            # TBank max rate: 600 pcs/min
from clients.abstract.client        import AbstractClient, SubscriptionType
from clients.abstract.instrument    import AbstractInstrument
from clients.abstract.interval      import IntervalIndex

from controls.abstract.source       import AbstractSource
from controls.abstract.data         import AbstractData
from controls.abstract.item         import AbstractItem

from classes.async_method           import AsyncMethod
from classes.event_method           import EventMethod
from classes.candlestick            import CandlestickData

from datetime                       import datetime, timedelta
from sortedcontainers               import SortedDict
from copy                           import deepcopy
from typing                         import List

import threading
import os

class Storage(AbstractSource):
    """ Класс хранилище данных """
    MAX_LOAD = 1440
    def __init__(self, client: AbstractClient, instrument: AbstractInstrument, load=True):
        self._path              = f"{os.getcwd()}\\data\\{client.name()}\\candles"
        self._fullname          = f"{self._path}\\{instrument.ticker}.bin"

        self._client            = client
        self._instrument        = instrument
        self._interval          = list(self._client.intervals())[0]                                                     # самый минимальный интервал

        self._last_price_lock   = threading.RLock()
        self._orderbook_lock    = threading.RLock()
        self._candles           = CandlestickData(self._instrument, self._interval)
        self._last_price        = 0.0
        self._orderbook         = []

        if load:
            self.load()

    def __del__(self):
        self.detach(None, SubscriptionType.LAST_PRICE)
        self.detach(None, SubscriptionType.ORDERBOOK)
        self.detach(None, SubscriptionType.CANDLE)
        self.save()

    def name(self):
        return self._instrument.ticker

    def reset(self):
        with self._candles as items: items.clear()
        with self._last_price_lock:  self._last_price = 0.0
        with self._orderbook_lock:   self._orderbook.clear()

    def load(self):
        """ Загрузка данных о свечах, стакане и прочем """
        os.makedirs(self._path, exist_ok=True)
        if os.path.exists(self._fullname):
            _type = self._client.CANDLE_ITEM_TYPE                                                                       # type: AbstractItem
            _size = _type.size()
            _dict = {}
            with open(self._fullname, 'rb') as f:
                while chunk := f.read(_size):
                    item = _type.restore(chunk)
                    _dict[item.index] = item
                with self._candles as items:
                    items.clear()
                    items.update(_dict)

        end   = datetime.now() + timedelta(minutes=10)
        start = self._candles[-1].index if len(self._candles) > 0 else None
        with self._last_price_lock:
            self._candles.load(self._interval, start, end, lambda value: setattr(self, "_last_price", value))
        self._load_orderbook()

        self.on_update_last_price.call()
        self.on_update_orderbook.call()
        self.on_update_candle.call()

    def save(self):
        with self._candles as items:
            with open(self._fullname, 'wb') as f:
                for item in items.values():
                    f.write(item.backup())

    def attach(self, callback, _type: SubscriptionType):
        """
        Подписка на события
        :param callback: функция обработчик с функцией вида func()
        :param _type: тип подписки
        """
        _id = self._instrument.uid
        match _type:
            case SubscriptionType.CANDLE:
                interval = self._interval.get(IntervalIndex.SUBSCRIPTION_INTERVAL)
                self.on_update_candle.subscribe(callback)
                self._client.attach(self.on_update_candle,     _id, SubscriptionType.CANDLE,    interval=interval)
            case SubscriptionType.ORDERBOOK:
                self.on_update_orderbook.subscribe(callback)
                self._client.attach(self.on_update_orderbook,  _id, SubscriptionType.ORDERBOOK, depth=50)
            case SubscriptionType.LAST_PRICE:
                self.on_update_last_price.subscribe(callback)
                self._client.attach(self.on_update_last_price, _id, SubscriptionType.LAST_PRICE)

    def detach(self, callback, _type: SubscriptionType):
        """
        Отписка от обновления данных
        :param callback: функция обработчик
        :param _type: тип подписки
        """
        _id = self._instrument.uid
        match _type:
            case SubscriptionType.CANDLE:
                self.on_update_candle.unsubscribe(callback)
                self._client.detach(self.on_update_candle,     _id, SubscriptionType.CANDLE)
            case SubscriptionType.ORDERBOOK:
                self.on_update_orderbook.unsubscribe(callback)
                self._client.detach(self.on_update_orderbook,  _id, SubscriptionType.ORDERBOOK)
            case SubscriptionType.LAST_PRICE:
                self.on_update_last_price.unsubscribe(callback)
                self._client.detach(self.on_update_last_price, _id, SubscriptionType.LAST_PRICE)

    @AsyncMethod
    def _load_orderbook(self, depth=50):
        """ Загрузка данных стакана """
        _list = self._instrument.orderbook(depth)
        with self._orderbook_lock:
            self._orderbook = _list

    def last_price(self) -> float:
        with self._last_price_lock:
            return self._last_price

    def orderbook(self) -> List[AbstractItem]:
        with self._orderbook_lock:
            return deepcopy(self._orderbook)

    def candlestick(self) -> AbstractData:
        return self._client.CANDLE_DATA_TYPE(self._candles)

    @EventMethod
    def on_update_candle(self, candle):
        _dict = { candle.index: candle }
        with self._candles as items:
            items.update(_dict)

    @EventMethod
    def on_update_last_price(self, price):
        with self._last_price_lock:
            self._last_price = price

    @EventMethod
    def on_update_orderbook(self, orderbook):
        with self._orderbook_lock:
            self._orderbook = orderbook