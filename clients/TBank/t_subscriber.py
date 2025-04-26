# t_subscriber_v2.py
from classes.sender import BackgroundSender


class TSubscriber:
    def __init__(self, sender: BackgroundSender, instrument_type):
        """
        Конструктор класса
        :param sender: объект, управляющей рассылкой данных
        :param instrument_type: ссылка на класс инструмента, объект которого будет создан в будущем
        """
        self._tag       = str(instrument_type.__name__)
        self._type      = instrument_type
        self._sender    = sender

    def attach(self, callback, _id, **kwargs):
        """
        Добавление подписки
        :param callback: синхронная функция, подписывающаяся на обновление данных
        :param _id: идентификатор инструмента, на который происходит подписка
        :param kwargs: именованные аргументы, которые зависят от типа инструмента
        """
        index = self._sender.attach(callback, self._tag, _id, kwargs)

    def detach(self, callback, _id):
        """
        Удаление подписки
        :param callback: синхронная функция, которая ранее подписывалась на обновление данных
        :param _id: идентификатор инструмента, от которого происходит отписка
        """
        self._sender.detach(callback, self._tag, _id)

    def empty(self):
        return self._sender.empty(self._tag)

    def instruments(self):
        """ Возвращает список инструментов для создания подписки """
        instruments = []
        for kwargs in self._sender.userdata(self._tag):
            instruments.append(self._type(**kwargs))
        return instruments

    def send(self, data, _id):
        self._sender.send(data, self._tag, _id)
