# abstract_client.py
from controls.abstract.source       import AbstractSource, AbstractObserver, AbstractInterval, SubscriptionType
from clients.abstract_instrument    import AbstractInstrument

class AbstractClient(AbstractSource):
    """ Абстрактный класс клиента с API сервера с котировками и прочим """
    def disconnect(self):
        """ Отключение от сервера """
        pass

    def connect(self):
        """ Переподключение к серверу """
        pass

    def attach(self, observer: AbstractObserver, _type : SubscriptionType):
        """ Добавить наблюдателя для подписки на событие обновления данных """
        pass

    def detach(self, observer: AbstractObserver, _type : SubscriptionType):
        """ Удалить наблюдателя из подписок на событие обновления данных """
        pass

    def instruments(self, buy_available=True):
        """
        Вывод инструментов
        :param buy_available: только доступные для покупки
        :return: возвращает список типа {"$ticker_name$": AbstractInstrument, ...]
        """
        pass

    def instrument(self, ticker) -> AbstractInstrument:
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
