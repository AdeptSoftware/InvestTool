# storage.py                                                                                                            # TBank max rate: 600 pcs/min
from clients.abstract.client        import AbstractClient, SubscriptionType
from clients.abstract.instrument    import AbstractInstrument
from clients.abstract.interval      import IntervalIndex

from controls.abstract.source       import AbstractSource
from controls.abstract.data         import AbstractData
from controls.abstract.item         import AbstractItem

from classes.async_method           import AsyncMethod
from controls.utils.event           import EventMethod
from classes.candlestick            import CandlestickData

from datetime                       import datetime, timedelta
from sortedcontainers               import SortedDict
from copy                           import deepcopy
from typing                         import List
from pathlib                        import Path
import threading
import os

def root():
    current = Path(__file__).parent
    while True:
        if (current / '.git').exists() or (current / 'requirements.txt').exists():
            return str(current)
        if current.parent == current:
            raise FileNotFoundError("Корень проекта не найден")
        current = current.parent

class Storage(AbstractSource):
    """ Класс хранилище данных """
    MAX_LOAD = 1440
    def __init__(self, client: AbstractClient, instrument: AbstractInstrument, update=True, readonly=False):
        self._path              = f"{root()}\\data\\{client.name()}\\candles"
        self._fullname          = f"{self._path}\\{instrument.ticker}.bin"
        self._readonly          = readonly

        self._client            = client
        self._instrument        = instrument
        self._interval          = list(self._client.intervals())[0]                                                     # самый минимальный интервал

        self._last_price_lock   = threading.RLock()
        self._orderbook_lock    = threading.RLock()
        self._candles           = CandlestickData(self._instrument, self._interval)
        self._last_price        = 0.0
        self._orderbook         = []

        self.load(update)
        self.attach(None, SubscriptionType.CANDLE)

    def __del__(self):
        self.detach(None, SubscriptionType.LAST_PRICE)
        self.detach(None, SubscriptionType.ORDERBOOK)
        self.detach(None, SubscriptionType.CANDLE)
        if not self._readonly:
            self.save()

    def name(self):
        return self._instrument.name

    def reset(self):
        self._candles.clear()
        with self._last_price_lock:  self._last_price = 0.0
        with self._orderbook_lock:   self._orderbook.clear()

    @AsyncMethod
    def load(self, update=True):
        """ Загрузка данных о свечах, стакане и прочем """
        if os.path.exists(self._fullname):
            os.makedirs(self._path, exist_ok=True)
            self._candles.deserialize(self._fullname, self._client.CANDLE_ITEM_TYPE)

        if update:
            with self._last_price_lock:
                self._candles.load(self._interval, None, lambda value: setattr(self, "_last_price", value))
            self._load_orderbook()

        self.on_update_last_price.notify()
        self.on_update_orderbook.notify()
        self.on_update_candle.notify()

    def save(self, filename=None):
        self._candles.serialize(filename or self._fullname)

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
                self.on_update_candle.connect(callback)
                self._client.attach(self.on_update_candle,     _id, SubscriptionType.CANDLE,    interval=interval)
            case SubscriptionType.ORDERBOOK:
                self.on_update_orderbook.connect(callback)
                self._client.attach(self.on_update_orderbook,  _id, SubscriptionType.ORDERBOOK, depth=50)
            case SubscriptionType.LAST_PRICE:
                self.on_update_last_price.connect(callback)
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
                self.on_update_candle.disconnect(callback)
                self._client.detach(self.on_update_candle,     _id, SubscriptionType.CANDLE)
            case SubscriptionType.ORDERBOOK:
                self.on_update_orderbook.disconnect(callback)
                self._client.detach(self.on_update_orderbook,  _id, SubscriptionType.ORDERBOOK)
            case SubscriptionType.LAST_PRICE:
                self.on_update_last_price.disconnect(callback)
                self._client.detach(self.on_update_last_price, _id, SubscriptionType.LAST_PRICE)

    @AsyncMethod
    def _load_orderbook(self, depth=50):
        """ Загрузка данных стакана """
        _list = self._instrument.orderbook(depth)
        with self._orderbook_lock:
            self._orderbook = _list

    def last_price(self) -> float:
        with self._last_price_lock:
            return float(self._last_price)

    def orderbook(self) -> List[AbstractItem]:
        with self._orderbook_lock:
            return deepcopy(self._orderbook)

    def candlestick(self) -> AbstractData:
        return self._client.CANDLE_DATA_TYPE(self._candles)

    @EventMethod
    def on_update_candle(self, candle):
        self._candles.update({ candle.index: candle })
        self.update()

    @EventMethod
    def on_update_last_price(self, price):
        with self._last_price_lock:
            self._last_price = price
        self.update()

    @EventMethod
    def on_update_orderbook(self, orderbook):
        with self._orderbook_lock:
            self._orderbook = orderbook
        self.update()

    @EventMethod
    def update(self, params=None):
        return