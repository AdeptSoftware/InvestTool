# source.py
from controls.abstract.data import AbstractData
from controls.abstract.item import AbstractItem
from typing                 import List

class AbstractSource:
    """ Абстрактный источник данных """

    def orderbook(self) -> List[AbstractItem]:
        pass

    def last_price(self) -> float:
        pass

    def candlestick(self) -> AbstractData:
        pass