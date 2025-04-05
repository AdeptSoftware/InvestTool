# t_subscriber.py
import threading

class TSubscriber:
    """ Класс для подписки на события изменения цены инструментов """
    def __init__(self, instrument_type):
        """
        Конструктор класса
        :param instrument_type: ссылка на класс инструмента, объект которого будет создан в будущем
        """
        self._lock        = threading.RLock()
        self._type        = instrument_type
        self._instruments = []

    def attach(self, fn, instrument_id, **kwargs):
        """
        Добавление подписки
        :param fn: функция, подписывающаяся на обновление данных
        :param instrument_id: индентификатор инструмента
        :param kwargs: дополнительные поля, которые зависят от типа инструмента
        """
        kwargs.update({"__delegate__": fn, "instrument_id": instrument_id})
        with self._lock:
            self._instruments += [ kwargs ]

    def detach(self, fn, instrument_id):
        """
        Удаление подписки
        :param fn: функция, которая ранее подписывалась на обновление данных
        :param instrument_id: индентификатор инструмента
        """
        with self._lock:
            for item in self._instruments:
                if item["__delegate__"] == fn and item["instrument_id"] == instrument_id:
                    self._instruments.remove(item)
                    break

    def is_empty(self):
        with self._lock:
            return len(self._instruments) == 0

    def instruments(self, **kwargs):
        """ Возвращает список инструментов для создания подписки """
        instruments = []
        with self._lock:
            ids = []
            for item in self._instruments:
                if item["instrument_id"] not in ids:
                    args = { k: v for k, v in item.items() if k[:2] != "__" }
                    args.update(kwargs)
                    instruments += [self._type(**args)]
                    ids += [item["instrument_id"]]
        return instruments

    def send(self, data, fn):
        """ Функция рассылки данных всем подписавшимся """
        if data:
            with self._lock:
                for item in self._instruments:
                    if item["instrument_id"] == data.instrument_uid:
                        item["__delegate__"](fn(data))

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()