# test_tinkoff_client.py
from tinkoff.invest                     import RequestError
from clients.TBank.t_stream_manager     import TStreamingManager
from clients.TBank.t_orderbook_data     import TOrderBookData
from clients.TBank.t_instrument         import TInstrument
from clients.TBank.t_interval           import TInterval
from clients.TBank.t_candlestick_data   import TCandlestickData, TCandlestickItem

from clients.abstract.client            import AbstractClient, SubscriptionType
from clients.abstract.instrument        import AbstractInstrument
from classes.rate_limiter import HybridRateLimiter
from clients.TBank.t_lazy_call          import LazyCall


class TClient(AbstractClient):
    CANDLE_ITEM_TYPE = TCandlestickItem
    CANDLE_DATA_TYPE = TCandlestickData

    def __init__(self, **kwargs):
        super().__init__()
        assert "token" in kwargs
        self._token                 = kwargs["token"]
        self._stream_manager        = TStreamingManager(self._token)
        self._limiter               = HybridRateLimiter(rpm=300, parallel=10, timeout=30)

        self._available_instruments = {}
        self._instruments           = {}

        self._limiter.start()
        self._get_instruments()

    def __del__(self):
        self.disconnect()
        self._limiter.shutdown()

    def name(self):
        return "tinkoff"

    def disconnect(self):
        """ Отключение от сервера """
        self._stream_manager.shutdown()

    def connect(self):
        """ Подключение к серверу """
        self._stream_manager.start()

    def reconnect(self):
        """ Переподключение к серверу """
        self._stream_manager.shutdown()
        self._stream_manager.start()

    def attach(self, callback, instrument_id, _type : SubscriptionType, **kwargs):
        """ Добавить наблюдателя для подписки на событие обновления данных """
        kwargs.update({ "instrument_id": instrument_id })
        match _type:
            case SubscriptionType.CANDLE:
                self._stream_manager.candle.attach(callback, instrument_id, **kwargs)
            case SubscriptionType.ORDERBOOK:
                self._stream_manager.orderbook.attach(callback, instrument_id, **kwargs)
            case SubscriptionType.LAST_PRICE:
                self._stream_manager.last_price.attach(callback, instrument_id, **kwargs)

    def detach(self, callback, instrument_id, _type : SubscriptionType):
        """ Удалить наблюдателя из подписок на событие обновления данных """
        match _type:
            case SubscriptionType.CANDLE:
                self._stream_manager.candle.detach(callback, instrument_id)
            case SubscriptionType.ORDERBOOK:
                self._stream_manager.orderbook.detach(callback, instrument_id)
            case SubscriptionType.LAST_PRICE:
                self._stream_manager.last_price.detach(callback, instrument_id)

    def find(self, ticker=None, class_code="TQBR"):
        """ Поиск идентификатора инструмента по его ticker """
        response = self._limiter(
            force   = False,
            func    = LazyCall(self._token, lambda cls: cls.instruments.find_instrument),
            query   = ticker
        )
        if response is not None:
            for item in response.instruments:
                if item.ticker == ticker and item.class_code == class_code:
                    return item.uid
        return None

    def _get_instruments(self):
        """ Определяет список общих и доступных инструментов """
        shares = self._limiter(
            force   = False,
            func    = LazyCall(self._token, lambda cls: cls.instruments.shares)
        )
        if shares is not None:
            for share in shares.instruments:
                instrument = TInstrument(self, share=share)
                self._instruments[share.ticker] = instrument
                if share.buy_available_flag:
                    self._available_instruments[share.ticker] = instrument

    def instrument(self, ticker, instrument_uid=None) -> AbstractInstrument:
        """
        Возвращает инструмент
        :param ticker: код инструмента
        :param instrument_uid: идентификатор инструмента
        :return: AbstractInstrument
        """
        if ticker:
            if ticker in self._instruments:
                return self._instruments[ticker]
        else:
            for ticker in self._instruments:
                if self._instruments[ticker].uid == instrument_uid:
                    return self._instruments[ticker]
        return None

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
        try:
            response = self._limiter(
                force           = False,
                func            = LazyCall(self._token, lambda cls: cls.market_data.get_candles),
                instrument_id   = instrument_id,
                interval        = interval,
                from_           = start,
                to              = end
            )
            return TCandlestickData.wrap(response.candles  if response   else None)
        except RequestError:
            instrument = self.instrument(None, instrument_id)
            print(f"[Candlestick]: Skip {instrument.ticker if instrument else instrument_id}")
            return TCandlestickData.wrap()

    def upload_orderbook(self, instrument_id, depth=50, **kwargs):
        try:
            response = self._limiter(
                force           = False,
                func            = LazyCall(self._token, lambda cls: cls.market_data.get_order_book),
                instrument_id   = instrument_id,
                depth           = depth
            )
            return TOrderBookData.wrap(response)
        except RequestError:
            instrument = self.instrument(None, instrument_id)
            print(f"[OrderBook]: Skip {instrument.ticker if instrument else instrument_id}")
            return TOrderBookData.wrap()