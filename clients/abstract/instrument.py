# instrument.py
from clients.abstract.client    import AbstractClient
from clients.abstract.interval  import AbstractInterval

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

    def candles(self, interval: AbstractInterval, start, end):
        pass

    def orderbook(self, depth=50):
        pass