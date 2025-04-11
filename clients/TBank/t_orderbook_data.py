# t_orderbook_data.py
from clients.TBank.t_quotation              import TQuotation
from controls.abstract.data                 import AbstractData
from controls.abstract.item                 import AbstractItem
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

    def value(self):
        return self.count

    @staticmethod
    def restore(obj):
        return None

    def backup(self):
        return None


class TOrderBookData(AbstractData):
    @staticmethod
    def wrap(raw_data):
        items = []
        # Продажи
        for item in raw_data.asks:
            items += [ TOrderBookItem(
                _price = item.price,
                _count = item.quantity,
                _type  = OrderType.ASK
            )]
        items.reverse()
        # Пустой элемент
        items += [ TOrderBookItem(
            _price = 0,
            _count = 0,
            _type  = OrderType.SEP
        )]
        # Покупки
        for item in raw_data.bids:
            items += [ TOrderBookItem(
                _price = TQuotation(item.price),
                _count = item.quantity,
                _type  = OrderType.BID
            )]
        return items
