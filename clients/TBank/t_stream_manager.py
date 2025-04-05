# t_stream_manager.py
from tinkoff.invest                 import Client, MarketDataRequest, SubscriptionAction, RequestError
from tinkoff.invest                 import SubscribeOrderBookRequest, OrderBookInstrument
from tinkoff.invest                 import SubscribeCandlesRequest, CandleInstrument, SubscriptionInterval
from tinkoff.invest                 import SubscribeLastPriceRequest, LastPriceInstrument
from clients.TBank.t_subscriber     import TSubscriber
from clients.TBank.t_orderbook_data import TOrderBookData
from clients.TBank.t_data           import TItem, TQuotation
import threading
import asyncio
import time

class TStreamingManager:
    def __init__(self, token):
        self._event     = threading.Event()                                                                             # Событие остановки
        self._thread    = None
        self._loop      = None
        self._delay     = 1

        self._token     = token
        self.last_price = TSubscriber(LastPriceInstrument)
        self.orderbook  = TSubscriber(OrderBookInstrument)
        self.candle     = TSubscriber(CandleInstrument)

    async def _thread_main(self):
        if self.orderbook.is_empty() and self.candle.is_empty():
            return

        def iterator():
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
            while not self._event.is_set():
                time.sleep(self._delay)

        def last_price(item):
            return TQuotation(item.price)

        def orderbook(data):
            return TOrderBookData(data)

        def candle(item):
            return TItem(item.time, item.open, item.close, item.high, item.low, item.volume)

        try:
            with Client(self._token) as client:
                for marketdata in client.market_data_stream.market_data_stream(iterator()):
                    if self._event.is_set():
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

    def start(self):
        self._event.clear()
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._thread = threading.Thread(target=self._run_thread, daemon=True)
        self._thread.start()

    def stop(self):
        self._event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread = None
        self._loop   = None

    def _run_thread(self):
        if self._loop:
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._thread_main())
            finally:
                try:
                    self._loop.close()
                except RuntimeError:
                    pass
                finally:
                    pass