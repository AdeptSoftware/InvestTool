# t_subscriber.py
from types       import FunctionType
from dataclasses import dataclass
from typing      import List
import threading

@dataclass
class _TSubscriberItem:
    callbacks:  List[FunctionType]
    uid:        int
    kwargs:     dict

class TSubscriber:
    """ Класс для подписки на события изменения цены инструментов """
    def __init__(self, instrument_type):
        """
        Конструктор класса
        :param instrument_type: ссылка на класс инструмента, объект которого будет создан в будущем
        """
        self._lock        = threading.RLock()
        self._type        = instrument_type
        self._instruments = []                                                                                          # type: List[_TSubscriberItem]

    def attach(self, callback, instrument_id, **kwargs):
        """
        Добавление подписки
        :param callback: функция, подписывающаяся на обновление данных
        :param instrument_id: индентификатор инструмента
        :param kwargs: дополнительные поля, которые зависят от типа инструмента
        """
        kwargs.update({"instrument_id": instrument_id})
        with self._lock:
            for item in self._instruments:
                if item.uid == instrument_id:
                    item.callbacks.append(callback)
                    return
            self._instruments.append(_TSubscriberItem([ callback ], instrument_id, kwargs))

    def detach(self, callback, instrument_id):
        """
        Удаление подписки
        :param callback: функция, которая ранее подписывалась на обновление данных
        :param instrument_id: индентификатор инструмента
        """
        with self._lock:
            for item in self._instruments:
                if item.uid == instrument_id:
                    if callback in item.callbacks:
                        item.callbacks.remove(callback)
                    if not item.callbacks:
                        self._instruments.remove(item)
                    return

    def is_empty(self):
        with self._lock:
            return len(self._instruments) == 0

    def instruments(self, **kwargs):
        """ Возвращает список инструментов для создания подписки """
        instruments = []
        with self._lock:
            for item in self._instruments:
                instruments.append(self._type(**item.kwargs))
        return instruments

    def send(self, data, fn_converter):
        """ Функция рассылки данных всем подписавшимся """
        if data:
            with self._lock:
                for item in self._instruments:
                    if item.uid == data.instrument_uid:
                        for callback in set(item.callbacks):
                            callback(fn_converter(data))
                        break

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()