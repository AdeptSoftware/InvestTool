# data.py
from controls.abstract.item import AbstractItem
from copy                   import deepcopy

class AbstractData:
    """
    Класс для манипуляций над данными\n
    * update(self, item)
    """
    def __init__(self, data, readonly=False):
        """
        Конструктор абстрактного класса
        :param data: данные для инициализации
        :param readonly: режим только для чтения
        """
        self._readonly = readonly
        self._data     = data

    def add(self, item: AbstractItem):
        """ Добавление нового элемента """
        assert (not self._readonly)
        assert (item is not None)
        self._data += [ item ]

    def replace(self, index, item: AbstractItem):
        """ Замена старых данных на новые """
        assert (not self._readonly)
        assert (item is not None)
        self._data[index] = item

    def clear(self):
        """ Очистка содержимого """
        assert (not self._readonly)
        self._data.clear()

    def remove(self, index):
        """ Удаление элемента по индексу """
        assert (not self._readonly)
        self._data.pop(index)

    def const(self, data=None):
        """ Создание объекта данных, изменение которых запрещено """
        instance = self.__class__.__new__(self.__class__)
        for k, v in self.__dict__.items():
            if k != "_data":
                setattr(instance, k, deepcopy(v))
        instance._data     = data or self._data
        instance._readonly = True
        return instance

    def update(self, item):
        """ Обновление данных по подписке """
        pass

    def max_text_width(self, ctx):
        """ Максимальная длина текста подписи по оси Y """
        pass

    def bounds(self):
        """ Границы значений по оси Y """
        pass

    def range(self):
        """ Диапазон значений по оси X """
        pass

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.const(self._data[index.start:index.stop:index.step])
        return deepcopy(self._data[index])

    def __iter__(self):
        for item in self._data:
            yield item
            #yield deepcopy(item)                                                                                       # !!! надо с этим что-то сделать