# t_stream_manager.py
from tinkoff.invest                     import Client, MarketDataRequest, SubscriptionAction, RequestError
from tinkoff.invest                     import SubscribeOrderBookRequest, OrderBookInstrument
from tinkoff.invest                     import SubscribeCandlesRequest, CandleInstrument, SubscriptionInterval
from tinkoff.invest                     import SubscribeLastPriceRequest, LastPriceInstrument
from clients.TBank.t_subscriber         import TSubscriber
from clients.TBank.t_orderbook_data     import TOrderBookData
from clients.TBank.t_candlestick_data   import TCandlestickItem, TQuotation
from classes.background_task            import BackgroundTask
from datetime                           import datetime, timedelta, UTC

import asyncio
import time

class TStreamingManager(BackgroundTask):
    def __init__(self, token):
        self._delay     = 1
        self._token     = token
        self.last_price = TSubscriber(LastPriceInstrument)
        self.orderbook  = TSubscriber(OrderBookInstrument)
        self.candle     = TSubscriber(CandleInstrument)
        super().__init__()

        self._offset    = timedelta(hours=datetime.now().hour - datetime.now(UTC).hour)

    def _run(self):
        """ Цикл обновления данных подписок """
        if self.orderbook.is_empty() and self.candle.is_empty():
            return

        def iterator():
            """ Итератор запросов """
            with self.candle:
                if not self.candle.is_empty():
                    yield MarketDataRequest(
                        subscribe_candles_request   = SubscribeCandlesRequest(
                            subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                            instruments             = self.candle.instruments(),
                            waiting_close           = True
                        )
                    )
            with self.orderbook:
                if not self.orderbook.is_empty():
                    yield MarketDataRequest(
                        subscribe_order_book_request= SubscribeOrderBookRequest(
                            subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                            instruments             = self.orderbook.instruments()
                        )
                    )
            with self.last_price:
                if not self.last_price.is_empty():
                    yield MarketDataRequest(
                        subscribe_last_price_request= SubscribeLastPriceRequest(
                            subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                            instruments             = self.last_price.instruments()
                        )
                    )
            while not self._stop_event.is_set():
                time.sleep(self._delay)

        def last_price(item):
            return TQuotation(item.price)

        def orderbook(data):
            return TOrderBookData.wrap(data)

        def candle(item):
            return TCandlestickItem(item.time + self._offset, item.open, item.close, item.high, item.low, item.volume)

        try:
            with Client(self._token) as client:
                for marketdata in client.market_data_stream.market_data_stream(iterator()):
                    if self._stop_event.is_set():
                        break

                    if marketdata.last_price:
                        self.last_price.send(marketdata.last_price, last_price)
                    if marketdata.orderbook:
                        self.orderbook.send(marketdata.orderbook, orderbook)
                    if marketdata.candle:
                        self.candle.send(marketdata.candle, candle)
        except asyncio.CancelledError as e:
            print(e)
        except RequestError as e:
            print(f"{e.code}: {e.details} -> {e.args}")
