# listener.py
import threading
import time

class Listener:
    def __init__(self, delay=0.25, start=False):
        self._stop_event = threading.Event()
        self._thread     = None
        self._delay      = delay

        self._lock       = threading.RLock()
        self._tickers    = []

        if start:
            self.start()

    def add(self, ticker):
        with self._lock:
            if ticker not in self._tickers:
                self._tickers += [ticker]

    def delete(self, ticker):
        with self._lock:
            if ticker in self._tickers:
                self._tickers.remove(ticker)

    def clear(self):
        with self._lock:
            self._tickers.clear()

    def tickers(self):
        with self._lock:
            for ticker in self._tickers:
                yield ticker

    def find(self, ticker_code):
        with self._lock:
            for ticker in self._tickers:
                if ticker.code == ticker_code:
                    yield ticker

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._loop)
            self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _loop(self):
        while not self._stop_event.is_set():
            with self._lock:
                for ticker in self._tickers:
                    ticker.update()
            time.sleep(self._delay)



