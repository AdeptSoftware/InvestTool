# item.py
from dataclasses    import dataclass
from typing         import Any

@dataclass
class AbstractItem:
    """
    Абстрактный класс элемента данных\n
    * merge(self, item)
    * __repr__(self)
    """

    def merge(self, item):
        """ Объединение данных """
        pass

    def index(self):
        pass