# t_instrument.py
from clients.abstract_instrument import AbstractInstrument, AbstractInterval
import requests
import json
import os

class TInstrument(AbstractInstrument):
    """ Класс финансового инструмента """
    def __init__(self, client, **kwargs):
        super().__init__(client)
        assert "share" in kwargs
        self._data = kwargs["share"]

    @property
    def name(self):
        return self._data.name

    @property
    def ticker(self):
        return self._data.ticker

    @property
    def uid(self):
        return self._data.uid

    def icon(self):
        """ Иконка инструмента """
        logo = self._data.brand.logo_name
        path = os.getcwd() + "/icons/"
        filename = path + logo
        os.makedirs(path, exist_ok=True)
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return f.read()
        else:
            res  = logo.split('.')
            url  = f"https://invest-brands.cdn-tinkoff.ru/{res[0]}x160.{res[1]}"
            response = requests.get(url)
            if response.status_code == 200:                                                                                     # noqa
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return response.content
        return None

    def properties(self):
        """ Список доступных свойств для чтения """
        _dict = {}
        for field in dir(self._data):
            if not field.startswith("_") and not callable(getattr(self._data, field)):
                _dict[field] = str(getattr(self._data, field))
        return _dict

    def create_request_candles(self, interval: AbstractInterval, start, end):
        """ Создает объект запроса для загрузки данных """
        return {"instrument_id": self._data.uid, "interval": interval.value[3], "start": start, "end": end,
                "__attach": {"interval": interval.value[4]}}

    def create_request_orderbook(self, depth=50):
        """ Создает объект запроса для загрузки данных """
        return {"instrument_id": self._data.uid, "depth": depth}