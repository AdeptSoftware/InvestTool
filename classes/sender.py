# sender.py
from typing             import Dict, List, Tuple, Callable
from classes.threads    import BackgroundTask
from collections        import deque
from copy               import copy

import threading
import traceback
import asyncio


class BackgroundSender(BackgroundTask):
    """ Класс, занимающийся рассылкой данных в отдельном потоке через асинхронные функции """
    def __init__(self):
        self._lock      = threading.RLock()
        self._queue     = deque()
        self._callbacks = {}                                                                                            # type: Dict[List[Tuple[Callable, object]]]
        self._stop_flag = True
        super().__init__()

    def shutdown(self):
        self._stop_flag = True
        super().shutdown()

    def start(self, timeout=5):
        if self._stop_flag:
            self._stop_flag = False
            super().start(timeout)

    async def _task(self):
        while not self._stop_flag:
            await asyncio.sleep(0.1)
            while not self._stop_flag and self._queue:
                tag, group, data = self._queue.popleft()
                with self._lock:
                    try:
                        for callback, _id, _ in self._callbacks[tag]:
                            if group == _id:
                                await self._loop.run_in_executor(None, callback, data)
                    except Exception:
                        print(traceback.format_exc())

    def attach(self, callback, tag, group=None, userdata=None) -> int:
        """
        Присоединяет объект к рассылке
        :param callback: синхронная функция, которая подписывается на события
        :param tag: тег, по которому происходит группировка функций
        :param group: идентификатор группы
        :param userdata: пользовательские данные (не идут в рассылку)
        :return: True/False - успешность выполнения
        """
        with self._lock:
            if tag not in self._callbacks:
                self._callbacks[tag] = []
            for func, _id, _ in self._callbacks[tag]:
                if callback == func and group == _id:
                    return False
            self._callbacks[tag].append((callback, group, userdata))
        return True

    def detach(self, callback, tag, group=None):
        """
        Отсоединяет объект от рассылки
        :param callback: синхронная функция, которая подписывалась на события
        :param tag: тег, по которому происходит группировка функций
        :param group: идентификатор группы
        :return: True/False - успешность выполнения
        """
        with self._lock:
            if tag in self._callbacks:
                index = 0
                for func, _id, userdata in self._callbacks[tag]:
                    if callback == func and group == _id:
                        self._callbacks[tag].pop(index)
                        return True
                    index += 1
        return False

    def empty(self, tag):
        with self._lock:
            if tag in self._callbacks:
                return len(self._callbacks[tag]) == 0
            return True

    def userdata(self, tag):
        """ Получить пользовательские данные """
        with self._lock:
            if tag in self._callbacks:
                for _, _, userdata in self._callbacks[tag]:
                    yield copy(userdata)

    def send(self, data, tag, group=None):
        with self._lock:
            self._queue.append((tag, group, data))