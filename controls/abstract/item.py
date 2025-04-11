# item.py
from dataclasses import dataclass

@dataclass
class AbstractItem:
    """
    Абстрактный класс элемента данных\n
    * __repr__(self)
    * restore(**kwargs)
    * backup()
    * index(self)
    * value(self)
    """

    @staticmethod
    def restore(data):
        pass

    def backup(self):
        pass

    @staticmethod
    def size():
        pass

    @property
    def index(self):
        return

    @property
    def value(self):
        return