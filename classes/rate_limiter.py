# rate_limiter.py
from classes.threads    import BackgroundTask
from typing             import Callable, Optional
from collections        import deque

import multiprocessing
import functools
import threading
import traceback
import asyncio
import time


class QueueItem:
    def __init__(self, func: Callable, args: tuple = None, kwargs: dict = None, future: Optional[asyncio.Future] = None):
        assert(func is not None)

        self.func   = func
        self.args   = args   or tuple()
        self.kwargs = kwargs or dict()
        self.future = future or asyncio.Future()

class AsyncRateLimiter:
    """ Асинхронный ограничитель с возможностью контроля количества одновременно выполняемых функций """
    def __init__(self, rpm, parallel: int = None, timeout: int = 30):
        """
        :param rpm: ограничение в минуту, шт/мин
        :param parallel: количество одновременно выполняемых функций, шт
        :param timeout: максимальное время выполнения функции, сек
        """
        self._interval      = 60 / rpm
        self._rpm           = rpm
        self._timeout       = timeout

        parallel            = parallel or max(1, multiprocessing.cpu_count() * 2)

        self._queue         = deque()
        self._timestamps    = deque()
        self._lock          = asyncio.Lock()
        self._semaphore     = asyncio.Semaphore(parallel)

        self._stop          = False
        self._task          = None

    async def shutdown(self):
        self._stop          = True
        await self._task

    @property
    def timeout(self):
        return self._timeout

    def call(self, force: bool, func: Callable, *args, **kwargs):
        """
        :param force: форсировать (вызов функции перемещается в начало очереди)
        :param func: вызываемая функция
        :param args: позиционные аргументы функции
        :param kwargs: именованные аргументы функции
        :return: Future-объект
        """
        item = QueueItem(func, args, kwargs)
        if force:
            self._queue.appendleft(item)
        else:
            self._queue.append(item)
        return item.future

    async def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    async def _run(self):
        while not self._stop:
            await asyncio.sleep(0.1)
            while not self._stop and self._queue:
                async with self._lock:
                    now = time.monotonic()
                    while self._timestamps and now - self._timestamps[0] >= 60:
                        self._timestamps.popleft()
                    if len(self._timestamps) >= self._rpm:
                        print(f"Достигнут лимит количества запросов. Ждем отката. Еще запросов в очереди: {len(self._queue)}")
                        await asyncio.sleep(self._interval)
                        continue

                    now = time.monotonic()
                    self._timestamps.append(now)
                    asyncio.create_task(self._handle(self._queue.popleft()))

    async def _handle(self, item: QueueItem):
        async with self._semaphore:
            try:
                if asyncio.iscoroutinefunction(item.func):
                    coro = item.func(*item.args, **item.kwargs)
                else:
                    loop = asyncio.get_running_loop()
                    coro = loop.run_in_executor(None, functools.partial(item.func, *item.args, **item.kwargs))
                result = await asyncio.wait_for(coro, self._timeout)
                item.future.set_result(result)
            except Exception:
                print(traceback.format_exc())


class HybridRateLimiter(BackgroundTask):
    """ (А)синхронный ограничитель с возможностью контроля количества одновременно выполняемых функций """
    def __init__(self, rpm, parallel: int = None, timeout: int = 30):
        """
        :param rpm: ограничение в минуту, шт/мин
        :param parallel: количество одновременно выполняемых функций, шт
        :param timeout: максимальное время выполнения функции, сек
        """
        super().__init__()
        self._limiter       = AsyncRateLimiter(rpm, parallel, timeout)
        self._event_ready   = threading.Event()
        self._task          = self._limiter.start

    def shutdown(self):
        asyncio.run_coroutine_threadsafe(self._limiter.shutdown(), self._loop)
        super().shutdown()

    def __call__(self, force: bool, func: Callable, *args, **kwargs):
        """
        :param force: форсировать (вызов функции перемещается в начало очереди)
        :param func: вызываемая функция
        :param args: позиционные аргументы функции
        :param kwargs: именованные аргументы функции
        :return: результат выполнения функции (или Future, если вызывается из асинхронного кода)
        """
        if asyncio.iscoroutinefunction(func):
            return self._limiter.call(force, func, *args, **kwargs)
        else:
            async def make_coroutine():
                return await self._limiter.call(force, func, *args, **kwargs)
            future = asyncio.run_coroutine_threadsafe(make_coroutine(), self._loop)

            try:
                return future.result(timeout=self._limiter.timeout)
            except Exception:
                print(traceback.format_exc())
            return None