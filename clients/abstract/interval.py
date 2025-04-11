# interval.py
from enum import Enum


class IntervalIndex(Enum):
    INDEX                   = 0     # int
    DESCRIPTION             = 1     # text
    COUNT                   = 2     # int (count of something... For example, minutes)
    MAX_DAYS                = 3     # int (maximum days when load)
    CANDLE_INTERVAL         = 4     # частота обновления свечей   (нативный тип источник)
    SUBSCRIPTION_INTERVAL   = 5     # частота обновления подписки (нативный тип источник)


class AbstractInterval(Enum):
    """ Абстрактный класс перечисления """
    @classmethod
    def cast(cls, index):
        """ Преобразование в объект класса """
        for item in cls:
            if item.get(IntervalIndex.INDEX) == index:
                return item
        raise ValueError(f"Элемента {cls.__name__} с индексом {index} не существует!")

    def get(self, index : IntervalIndex):
        return self.value[index.value]