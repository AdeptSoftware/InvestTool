# t_candlestick_data.py
from controls.abstract.data     import AbstractData
from controls.abstract.item     import AbstractItem
from clients.TBank.t_quotation  import TQuotation
from dataclasses                import dataclass
import datetime
import struct

@dataclass
class TCandlestickItem(AbstractItem):
    date:       datetime.datetime
    open:       TQuotation
    close:      TQuotation
    low:        TQuotation
    high:       TQuotation
    volume:     int

    def __init__(self, _date, _open, _close, _low, _high, _volume):
        self.date   = _date.replace(tzinfo=None)
        self.open   = TQuotation(_open)
        self.close  = TQuotation(_close)
        self.low    = TQuotation(_low)
        self.high   = TQuotation(_high)
        self.volume = _volume

    def __repr__(self):
        return f"{self.date.strftime("%D %H:%M")}\n" \
               f"o: {self.open}\nc: {self.close}\nl: {self.low}\nh: {self.high}\nv: {self.volume}"

    @staticmethod
    def restore(data):
        timestamp, open_, close, low, high, volume = struct.unpack("<d d d d d q", data)
        date = datetime.datetime.fromtimestamp(timestamp)
        return TCandlestickItem(date, open_, close, low, high, volume)

    def backup(self):
        timestamp = self.date.timestamp()
        return struct.pack("<d d d d d q",
                           timestamp,
                           self.open,
                           self.close,
                           self.low,
                           self.high,
                           self.volume)

    @staticmethod
    def size():
        return struct.calcsize('<d d d d d q')

    """
        return {
            "date":     self.date.isoformat(),
            "open":     float(self.open),
            "close":    float(self.close),
            "low":      float(self.low),
            "high":     float(self.high),
            "volume":   self.volume
        }
    """

    @property
    def index(self):
        return self.date

    @property
    def value(self):
        return self.close

class TCandlestickData(AbstractData):
    @staticmethod
    def wrap(raw_data=None):
        items = []
        if raw_data:
            delta = datetime.timedelta(hours=datetime.datetime.now().hour - datetime.datetime.now(datetime.UTC).hour)
            for item in raw_data:
                items += [TCandlestickItem(
                    _date=item.time + delta,
                    _open=item.open,
                    _close=item.close,
                    _high=item.high,
                    _low=item.low,
                    _volume=item.volume
                )]
        return items

    def max_text_width(self, ctx):
        """ Максимальная длина текста подписи по оси Y """
        c_max = 0
        for candle in self._data:
            c_max = max(
                ctx.text_width(str(candle.close)),
                ctx.text_width(str(candle.high)),
                ctx.text_width(str(candle.low)),
                ctx.text_width(str(candle.open))
            )
        return c_max

    def bounds(self):
        """ Границы значений по оси Y """
        y_min = y_max = None
        for candle in self._data:
            y_min = min(y_min or candle.low,  candle.low)
            y_max = max(y_max or candle.high, candle.high)
        return y_min, y_max

    def range(self):
        """ Диапазон значений по оси X """
        y_min = y_max = None
        for candle in self._data:
            y_min = min(y_min or candle.low,  candle.low)
            y_max = max(y_max or candle.high, candle.high)
        return y_min, y_max