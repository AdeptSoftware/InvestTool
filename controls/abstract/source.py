# source.py
from controls.abstract.observer import AbstractObserver
from controls.abstract.interval import AbstractInterval
from enum                       import Enum

class SubscriptionType(Enum):
    CANDLE      = 0
    ORDERBOOK   = 1
    LAST_PRICE  = 2


class AbstractSource:
    """
    Абстрактный класс источника данных\n
    * upload(interval, start, end)
    * intervals(self)
    * attach(observer: AbstractObserver)
    * detach(observer: AbstractObserver)
    """
    def attach(self, observer: AbstractObserver, _type : SubscriptionType, **kwargs):
        """ Добавить наблюдателя для подписки на событие обновления данных """
        pass

    def detach(self, observer: AbstractObserver, _type : SubscriptionType):
        """ Удалить наблюдателя из подписок на событие обновления данных """
        pass

    @staticmethod
    def intervals():
        """
        Доступные интевалы для загрузки
        :return: Возвращает класс, порожденный от AbstractInterval
        """
        pass

    def upload_candles(self, **kwargs):
        """
        Загрузка данных\n
        Должна быть предусмотрена загрузка данных по умолчанию для первичной инициализации
        """
        pass

    def upload_orderbook(self, **kwargs):
        """
        Загрузка данных\n
        Должна быть предусмотрена загрузка данных по умолчанию для первичной инициализации
        """
        pass