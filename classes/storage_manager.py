# storage_manager.py
from clients.abstract.client import AbstractClient
from classes.storage         import Storage

class StorageManager:
    """ Класс, хранящий все хранилища с данными """
    def __init__(self, client: AbstractClient):
        self._client = client
        self._items  = {}

        instruments = self._client.instruments(buy_available=True)
        for ticker, instrument in instruments.items():
            self._items[ticker] = Storage(self._client, instrument)

    def __del__(self):
        self._client.disconnect()

    @property
    def client(self) -> AbstractClient:
        return self._client

    def get(self, ticker):
        return self._items[ticker]