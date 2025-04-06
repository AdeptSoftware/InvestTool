# t_data.py
from controls.abstract.data     import AbstractData, AbstractItem
from clients.TBank.t_quotation  import TQuotation
from dataclasses                import dataclass
import datetime

@dataclass
class TItem(AbstractItem):
    date:       datetime.datetime
    open:       TQuotation
    close:      TQuotation
    low:        TQuotation
    high:       TQuotation
    volume:     int

    def __init__(self, _date, _open, _close, _low, _high, _volume):
        offset = datetime.timedelta(hours=datetime.datetime.now().hour - datetime.datetime.now(datetime.UTC).hour)
        self.date   = _date + offset
        self.open   = TQuotation(_open)
        self.close  = TQuotation(_close)
        self.low    = TQuotation(_low)
        self.high   = TQuotation(_high)
        self.volume = _volume

    def __repr__(self):
        return f"{self.date.strftime("%D %H:%M")}\n" \
               f"o:\t{self.open}\nc:\t{self.close}\nl:\t{self.low}\nh:\t{self.high}\nv:\t{self.volume}"

    def merge(self, item):
        """ Объединение данных """
        self.close   = item.close
        self.high    = max(self.high, item.high)
        self.low     = min(self.low,  item.low)
        self.volume += item.volume

    def index(self):
        return self.date

class TData(AbstractData):
    def __init__(self, data, readonly=False):
        """
        Конструктор класса
        :param data: данные для инициализации
        :param readonly: режим только для чтения
        """
        _data = []
        for item in data:
            _data += [ TItem(
                _date   = item.time,
                _open   = item.open,
                _close  = item.close,
                _high   = item.high,
                _low    = item.low,
                _volume = item.volume
            )]
        super().__init__(_data, readonly)

    def update(self, item: TItem):
        """
        Обновление данных по подписке
        :param item: новый элемент
        """
        assert (not self._readonly)
        assert (item is not None)
        if self._data:
            if self._data[-1].date.hour   == item.date.hour and \
               self._data[-1].date.minute == item.date.minute:
                self._data[-1].merge(item)
                return
        self._data += [ item ]

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
            y_min = min(y_min or candle.low, candle.low)
            y_max = max(y_max or candle.high, candle.high)
        return y_min, y_max