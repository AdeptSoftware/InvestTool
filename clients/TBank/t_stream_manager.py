# t_stream_manager.py
from tinkoff.invest                     import Client, MarketDataRequest, SubscriptionAction, RequestError
from tinkoff.invest                     import SubscribeOrderBookRequest, OrderBookInstrument
from tinkoff.invest                     import SubscribeCandlesRequest, CandleInstrument, SubscriptionInterval
from tinkoff.invest                     import SubscribeLastPriceRequest, LastPriceInstrument

from classes.sender                     import BackgroundSender
from clients.TBank.t_subscriber         import TSubscriber
from clients.TBank.t_orderbook_data     import TOrderBookData
from clients.TBank.t_candlestick_data   import TCandlestickItem, TQuotation
from classes.threads                    import BackgroundThread

from datetime                           import datetime, timedelta, UTC
from threading                          import Event

import traceback
import time

class TStreamingManager(BackgroundThread):
    def __init__(self, token):
        self._token         = token
        self._sender        = BackgroundSender()
        self.last_price     = TSubscriber(self._sender, LastPriceInstrument)
        self.orderbook      = TSubscriber(self._sender, OrderBookInstrument)
        self.candle         = TSubscriber(self._sender, CandleInstrument)
        self._stop_event    = Event()
        self._delay         = 1
        self._sender.start()
        super().__init__()

        self._offset        = timedelta(hours=datetime.now().hour - datetime.now(UTC).hour)

    def __del__(self):
        self._sender.shutdown()

    def start(self):
        self._stop_event.clear()
        super().start()

    def shutdown(self):
        self._stop_event.set()
        super().shutdown()

    def _main(self):
        """ Цикл обновления данных подписок """
        if self.orderbook.empty() and self.candle.empty():
            return

        def iterator():
            """ Итератор запросов """
            if not self.candle.empty():
                yield MarketDataRequest(
                    subscribe_candles_request   = SubscribeCandlesRequest(
                        subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                        instruments             = self.candle.instruments(),
                        waiting_close           = True
                    )
                )
            if not self.orderbook.empty():
                yield MarketDataRequest(
                    subscribe_order_book_request= SubscribeOrderBookRequest(
                        subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                        instruments             = self.orderbook.instruments()
                    )
                )
            if not self.last_price.empty():
                yield MarketDataRequest(
                    subscribe_last_price_request= SubscribeLastPriceRequest(
                        subscription_action     = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                        instruments             = self.last_price.instruments()
                    )
                )
            while not self._stop_event.is_set():
                time.sleep(self._delay)

        def convert_lp(item):
            return TQuotation(item.price)

        def convert_ob(item):
            return TOrderBookData.wrap(item)

        def convert_cd(item):
            return TCandlestickItem(item.time + self._offset, item.open, item.close, item.high, item.low, item.volume)

        try:
            with Client(self._token) as client:
                for marketdata in client.market_data_stream.market_data_stream(iterator()):
                    if self._stop_event.is_set():
                        break

                    if marketdata.last_price:
                        self.last_price.send(convert_lp(marketdata.last_price), marketdata.last_price.instrument_uid)
                    if marketdata.orderbook:
                        self.orderbook.send(convert_ob(marketdata.orderbook), marketdata.orderbook.instrument_uid)
                    if marketdata.candle:
                        self.candle.send(convert_cd(marketdata.candle), marketdata.candle.instrument_uid)
        except Exception:
            print(traceback.format_exc())
