# t_orderbook_data.py
from clients.TBank.t_quotation              import TQuotation
from controls.abstract.data                 import AbstractData
from controls.abstract.item                 import AbstractItem
from dataclasses                            import dataclass

@dataclass
class TOrderBookItem(AbstractItem):
    price:      TQuotation
    count:      int

    def __init__(self, _price, _count):
        self.price = TQuotation(_price)
        self.count = _count

    def __repr__(self):
        return f"{self.price}: {self.count}"

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
    def wrap(raw_data=None):
        items = [[], []]
        if raw_data:
            # Продажи
            for item in raw_data.asks:
                items[0]  += [ TOrderBookItem(
                    _price = item.price,
                    _count = item.quantity
                )]
            items[0].reverse()
            # Покупки
            for item in raw_data.bids:
                items[1]  += [ TOrderBookItem(
                    _price = TQuotation(item.price),
                    _count = item.quantity
                )]
        return items
