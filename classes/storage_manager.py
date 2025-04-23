# storage_manager.py
from clients.abstract.client import AbstractClient
from classes.storage         import Storage, SubscriptionType

class StorageManager:
    """ Класс, хранящий все хранилища с данными """
    def __init__(self, client: AbstractClient):
        self._client = client
        self._items  = {}

    def __del__(self):
        self._client.disconnect()

    def items(self):
        return self._items.values()

    @property
    def client(self) -> AbstractClient:
        return self._client

    def get(self, ticker):
        if ticker in self._items:
            return self._items[ticker]
        instrument = self._client.instrument(ticker)
        if instrument:
            self._items[ticker] = Storage(self._client, instrument, update=True)
            return self._items[ticker]
        return None