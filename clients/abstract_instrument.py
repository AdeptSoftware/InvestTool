# abstract_instrument.py
from clients.abstract_client import AbstractInterval

class AbstractInstrument:
    """ Абстрактный класс финансового инструмента """
    def __init__(self, client):
        self._client : AbstractClient = client

    @property
    def ticker(self):                                                                                                   # noqa
        pass

    @property
    def name(self):                                                                                                     # noqa
        pass

    def icon(self):
        """ Иконка инструмента """
        pass

    def properties(self):
        """ Список доступных свойств для чтения """
        pass

    def create_request_candles(self, interval: AbstractInterval, start, end):
        """ Создает объект запроса для загрузки данных """
        pass

    def create_request_orderbook(self, depth=50):
        """ Создает объект запроса для загрузки данных """
        pass