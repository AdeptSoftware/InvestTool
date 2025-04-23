# candlestick.py
from classes.async_method           import AsyncMethod
from controls.abstract.item         import AbstractItem
from clients.abstract.instrument    import AbstractInstrument
from clients.abstract.interval      import AbstractInterval, IntervalIndex

from datetime                       import datetime, timedelta, date, time
from sortedcontainers               import SortedDict
from threading                      import RLock
from typing                         import List

class CandlestickData(object):
    def __init__(self, instrument: AbstractInstrument, interval: AbstractInterval, _dict=None):
        self._instrument    = instrument
        self._interval      = interval
        self._data          = SortedDict(_dict or {})
        self._updated       = self._data.peekitem(-1)[0] if self._data else datetime.min
        self._lock          = RLock()

    def __len__(self):
        # with self._lock:
        return len(self._data)

    def __iter__(self) -> AbstractItem:
        with self._lock:
            for item in self._data:
                yield item

    def __getitem__(self, index) -> List[AbstractItem] | AbstractItem:
        with self._lock:
            if isinstance(index, int):
                self._auto(self.__normalize(index), False)
                return self._data.peekitem(index)[1]
            elif isinstance(index, datetime):
                self._auto(index, True)
                return self._data[index]
            elif isinstance(index, slice):
                if isinstance(index.start, int) or isinstance(index.stop, int) or isinstance(index.step, int):
                    self._auto(min(
                        self.__normalize(index.start) if index.start else 0,
                        self.__normalize(index.stop)  if index.stop  else len(self._data) - 1
                    ), False)
                    return list(self._data.values())[index.start:index.stop:index.step]
                elif isinstance(index.start, datetime) or isinstance(index.stop, datetime):
                    start = index.start if index.start else self._data.peekitem(0)[0]
                    stop  = index.stop  if index.stop  else self._data.peekitem(-1)[0]
                    self._auto(min(start, stop), True)
                    return [self._data[key] for key in self._data.irange(start, stop)]
            raise TypeError(f"Unsupported index type: {str(type(index))}")

    def __normalize(self, index):
        """
        Нормализация индекса от 0 до len(self._data)-1.
        Если значение становится отрицательным, то требуется дозагрузка данных
        """
        return index if index >= 0 else len(self._data) + index

    def _auto(self, index, is_datetime_type):
        """
        Дозагрузка данных
        :param index: должен быть нормализован относительно общего числа элементов
        :param is_datetime_type: выбор логики поведения в заивисимости от типа
        :return:
        """
        # Вызывается всегда под self._lock
        if is_datetime_type:
            self.load.sync(self._interval, index)
        elif index < 0:
            length     = len(self._data)
            delta      = timedelta(days=self._interval.get(IntervalIndex.MAX_DAYS))
            while index < 0:
                end    = self._data.peekitem(0)[1].index if length > 0 else datetime.now()
                start  = end - delta
                if not self.load.sync(self._interval, start) or len(self._data) - length == 0:
                    break                                                                                               # больше данных нет
                index += len(self._data) - length
                length = len(self._data)

    @AsyncMethod
    def load(self, interval, start, last_price_callback=None):
        """
        Загрузчик данных
        :param interval: объект интервала для уточнения загружаемого максимально допустимого количества дней
        :param start: дата начала данных
        :param last_price_callback: функция, с помощью которой будет возвращена информация о последней цене
        :return: достигнут ли конец данных (True/False)
        """
        first = last = None
        with self._lock:
            if self._data:
                first = self._data.peekitem( 0)[0]
                last  = self._data.peekitem(-1)[0]

        delta = timedelta(days=interval.get(IntervalIndex.MAX_DAYS))
        now   = datetime.now()
        end   = now
        flag  = len(self._data) == 0    # Флаг загрузки свежих данных
        if first:
            if start is None or start > first:
                start = last
                flag  = True
            else:
                end   = first
                start = start if end - start > delta else end - delta
        elif start is None:
            start = end - delta
        start = start.replace(tzinfo=None)
        end   = end.replace(tzinfo=None)

        with self._lock:
            _min = timedelta(minutes=1)
            if (                  _min > end - start        ) or \
               (flag and last and _min > end - last         ) or \
               (flag and          _min > end - self._updated):
                return True

        # print(f"{self._instrument.ticker} [{last}, {self._updated}]: {start} {end}")

        _date = start
        while _date < end:
            _list = self._instrument.candles(interval, _date, _date+delta)
            if len(_list) == 0:
                self._updated = min(_date+delta, now) if flag else self._updated
                return False
            _dict = { item.index: item for item in _list }
            with self._lock:
                self._data.update(_dict)
                if last_price_callback:
                    last_price_callback(self._data.peekitem(-1)[1].value)
                _date += delta
                if flag:
                    self._updated = min(_date, now)
        return True

    def update(self, _dict):
        with self._lock:
            self._data.update(_dict)
            self._updated = max(self._updated, self._data.peekitem(-1)[0])

    def clear(self):
        with self._lock:
            self._data.clear()
            self._updated = datetime.min

    def serialize(self, filename):
        with self._lock:
            with open(filename, 'wb') as f:
                for item in self._data.values():
                    f.write(item.backup())

    def deserialize(self, filename, _type: AbstractItem):
        _dict = {}
        _size = _type.size()
        with open(filename, 'rb') as f:
            while chunk := f.read(_size):
                item = _type.restore(chunk)
                _dict[item.index] = item

        with self._lock:
            self._data.clear()
            self._data.update(_dict)
            self._updated = self._data.peekitem(-1)[0] if self._data else datetime.min