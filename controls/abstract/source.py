# source.py
from controls.abstract.data     import AbstractData
from controls.abstract.item     import AbstractItem
from controls.abstract.model    import AbstractModel
from typing                     import List

class AbstractSource(AbstractModel):
    """ Абстрактный источник данных """

    def orderbook(self) -> List[AbstractItem]:
        pass

    def last_price(self) -> float:
        pass

    def candlestick(self) -> AbstractData:
        pass