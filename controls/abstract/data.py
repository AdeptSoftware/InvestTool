# data.py
from __future__             import annotations
from controls.abstract.item import AbstractItem
from copy                   import copy

class AbstractData:
    def __init__(self, data: object):
        self._data = data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for item in self._data:
            yield copy(item)

    def __getitem__(self, index) -> "AbstractData" | AbstractItem:
        if isinstance(index, slice):
            return self._const(self._data[index])
        return copy(self._data[index])

    def __bool__(self):
        return len(self._data) != 0

    def _const(self, data):
        instance = self.__class__.__new__(self.__class__)
        instance._data = data
        return instance

    def max_text_width(self, ctx):
        """ Максимальная длина текста подписи по оси Y """
        pass

    def bounds(self):
        """ Границы значений по оси Y """
        pass

    def range(self):
        """ Диапазон значений по оси X """
        pass