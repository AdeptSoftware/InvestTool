# item.py
from dataclasses import dataclass

@dataclass
class AbstractItem:
    """
    Абстрактный класс элемента данных\n
    * merge(self, item)
    * __repr__(self)
    """
    pass

    def merge(self, item):
        """ Объединение данных """
        pass