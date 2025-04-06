# t_orderbook_data.py
from clients.TBank.t_quotation              import TQuotation
from controls.abstract.data                 import AbstractData, AbstractItem
from controls.orderbook.orderbook_renderer  import OrderType
from dataclasses                            import dataclass

@dataclass
class TOrderBookItem(AbstractItem):
    price:      TQuotation
    count:      int
    type:       OrderType

    def __init__(self, _price, _count, _type):
        self.price = TQuotation(_price)
        self.count = _count
        self.type  = _type

    def __repr__(self):
        return f"[bid={self.type}] {self.price}: {self.count}"

    def index(self):
        return self.price

class TOrderBookData(AbstractData):
    def __init__(self, data):
        """
        Конструктор класса
        :param data: данные для инициализации
        """
        _data = []
        # Продажи
        for item in data.asks:
            _data     +=[TOrderBookItem(
                _price = item.price,
                _count = item.quantity,
                _type  = OrderType.ASK
            )]
        _data.reverse()
        # Пустой элемент
        _data         +=[TOrderBookItem(
                _price = 0,
                _count = 0,
                _type  = OrderType.SEP
        )]
        # Покупки
        for item in data.bids:
            _data     +=[TOrderBookItem(
                _price = TQuotation(item.price),
                _count = item.quantity,
                _type  = OrderType.BID
            )]
        super().__init__(_data)
        self.last_price = (hasattr(data, "last_price") and TQuotation(data.last_price)) or None

    def update(self, item: TOrderBookItem):
        """
        Обновление данных по подписке
        :param item: новый последняя цена сделки
        """
        assert (not self._readonly)
        assert (item is not None)
        self._data += [ item ]