# client.py
from enum import Enum


class SubscriptionType(Enum):
    CANDLE      = 0
    ORDERBOOK   = 1
    LAST_PRICE  = 2


class AbstractClient:
    """ Абстрактный класс клиента с API сервера с котировками и прочим """
    CANDLE_ITEM_TYPE = None
    CANDLE_DATA_TYPE = None

    def disconnect(self):
        """ Отключение от сервера """
        pass

    def connect(self):
        """ Подключение к серверу """
        pass

    def reconnect(self):
        """ Переподключение к серверу """
        pass

    def name(self):
        pass

    def attach(self, callback, _id, _type : SubscriptionType, **kwargs):
        """ Добавить наблюдателя для подписки на событие обновления данных """
        pass

    def detach(self, callback, _id, _type : SubscriptionType):
        """ Удалить наблюдателя из подписок на событие обновления данных """
        pass

    def instruments(self, buy_available=True):
        """
        Вывод инструментов
        :param buy_available: только доступные для покупки
        :return: возвращает список типа {"$ticker_name$": AbstractInstrument, ...]
        """
        pass

    def instrument(self, ticker):
        """
        Возвращает инструмент
        :param ticker: код инструмента
        :return: AbstractInstrument
        """
        pass

    @staticmethod
    def intervals():
        """
        Доступные интевалы для загрузки
        :return: Возвращает класс, порожденный от AbstractChartInterval
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
