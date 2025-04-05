# t_client.py
from tinkoff.invest                 import Client
from clients.abstract_client        import AbstractClient, AbstractObserver, SubscriptionType
from clients.TBank.t_stream_manager import TStreamingManager
from clients.TBank.t_orderbook_data import TOrderBookData
from clients.TBank.t_instrument     import TInstrument
from clients.TBank.t_interval       import TInterval
from clients.TBank.t_data           import TData
import threading
import asyncio
import time


class TClient(AbstractClient):
    def __init__(self, **kwargs):
        super().__init__()
        assert "token" in kwargs
        self._token                 = kwargs["token"]
        self._stream_manager        = TStreamingManager(self._token)

        self._available_instruments = {}
        self._instruments           = {}
        self._get_instruments()

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        """ Отключение от сервера """
        self._stream_manager.stop()

    def connect(self):
        """ Переподключение к серверу """
        self._stream_manager.start()

    def attach(self, observer: AbstractObserver, _type : SubscriptionType, **kwargs):
        """ Добавить наблюдателя для подписки на событие обновления данных """
        match _type:
            case SubscriptionType.CANDLE:
                self._stream_manager.candle.attach(observer.update, observer.target().uid, **kwargs)
            case SubscriptionType.ORDERBOOK:
                self._stream_manager.orderbook.attach(observer.update, observer.target().uid, **kwargs)
            case SubscriptionType.LAST_PRICE:
                self._stream_manager.last_price.attach(observer.update, observer.target().uid, **kwargs)

    def detach(self, observer: AbstractObserver, _type : SubscriptionType):
        """ Удалить наблюдателя из подписок на событие обновления данных """
        match _type:
            case SubscriptionType.CANDLE:
                self._stream_manager.candle.detach(observer.update, observer.target().uid)
            case SubscriptionType.ORDERBOOK:
                self._stream_manager.orderbook.detach(observer.update, observer.target().uid)
            case SubscriptionType.LAST_PRICE:
                self._stream_manager.last_price.detach(observer.update, observer.target().uid)

    def find(self, ticker, class_code="TQBR"):
        """ Поиск идентификатора инструмента по его ticker """
        with Client(self._token) as client:
            response = client.instruments.find_instrument(query=ticker)
            for item in response.instruments:
                if item.ticker == ticker and item.class_code == class_code:
                    return item.uid
        return None

    def _get_instruments(self):
        """ Определяет список общих и доступных инструментов """
        with Client(self._token) as client:
            for share in client.instruments.shares().instruments:
                instrument = TInstrument(self, share=share)
                self._instruments[share.ticker] = instrument
                if share.buy_available_flag:
                    self._available_instruments[share.ticker] = instrument

    def instrument(self, ticker):
        """
        Возвращает инструмент
        :param ticker: код инструмента
        :return: AbstractInstrument
        """
        assert ticker in self._instruments
        return self._instruments[ticker]

    def instruments(self, buy_available=True):
        """
        Вывод инструментов
        :param buy_available: только доступные для покупки
        :return: возвращает список типа {"$ticker_name$": AbstractInstrument, ...]
        """
        if buy_available:
            return self._available_instruments
        return self._instruments

    @staticmethod
    def intervals():
        """
        Доступные интевалы для загрузки
        :return: Возвращает класс, порожденный от AbstractChartInterval
        """
        return TInterval

    def upload_candles(self, instrument_id, interval, start, end, **kwargs):
        with Client(self._token) as client:
            response            = client.market_data.get_candles(
                instrument_id   = instrument_id,
                interval        = interval,
                from_           = start,
                to              = end
            )
            return TData(response.candles)

    def upload_orderbook(self, instrument_id, depth=50, **kwargs):
        with Client(self._token) as client:
            response            = client.market_data.get_order_book(
                instrument_id   = instrument_id,
                depth           = depth
            )
            return TOrderBookData(response)