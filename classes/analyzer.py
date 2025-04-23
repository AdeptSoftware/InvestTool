# analyzer.py
from classes.storage_manager import StorageManager, Storage
from controls.abstract.data  import AbstractData
from datetime                import datetime
import asyncio
import math

class DataAnalyzer:
    def __init__(self, manager: StorageManager):
        self._manager = manager

    def dynamic(self, start: datetime, end: datetime):
        async def _main():
            price         = []
            delta         = []
            percent       = []
            acceleration  = []
            determination = []

            tasks         = [ self._process(storage, start, end) for storage in self._manager.items() ]
            result        = await asyncio.gather(*tasks)

            for res in result:
                _price, _delta, _percent, _acceleration, _determination = res
                determination.append(_determination)
                acceleration.append(_acceleration)
                percent.append(_percent)
                delta.append(_delta)
                price.append(_price)
            return price, delta, percent, acceleration, determination
        return asyncio.run(_main())

    async def _process(self, storage, start: datetime, end: datetime):
        candles = storage.candlestick()
        items = candles[start:end]
        _price = storage.last_price()
        _delta, _percent = self._profit(items)
        _acceleration, _determination = self._trend(items)
        return _price, _delta, _percent, _acceleration, _determination

    @staticmethod
    def _profit(items):
        if items:
            delta   = items[-1].value - items[0].value
            percent = round((delta / items[0].value) * 100, 2)
            return delta, percent
        return 0, 0

    @staticmethod
    def _trend(items):
        if not items:
            return 0, 0

        sum_x  = 0
        sum_y  = 0
        sum_xy = 0
        sum_xx = 0
        min_x  = items[0].index.timestamp() - 1
        for item in items:
            x = item.index.timestamp() - min_x
            sum_x  += x
            sum_y  += item.value
            sum_xy += item.value * x
            sum_xx += x * x
        # y'(x) = kx + b
        n = len(items)
        try:
            k = ((n * sum_xy) - (sum_x * sum_y)) / ((n * sum_xx) - (sum_x * sum_x))
        except ZeroDivisionError:
            k = 1.0
        b = (sum_y - (k * sum_x)) / n

        sum_y1 = 0      # sum((y(i) - y'(i))^2)
        sum_y2 = 0      # sum((y(i) - average)^2)
        average  = sum_y / n
        for item in items:
            x = item.index.timestamp() - min_x
            sum_y1 += math.pow(item.value - ((k * x) + b), 2)
            sum_y2 += math.pow(item.value - average, 2)
        r2 = 1 - (sum_y1 / sum_y2) if sum_y2 != 0 else 0
        return k, r2    # acceleration, determination