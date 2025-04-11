# async_method.py
from functools      import wraps
from classes.trace  import trace

import threading
import asyncio

class AsyncMethod:
    """ Декоратор для запуска синхронных методов в асинхронном режиме """
    def __init__(self, func):
        self.func   = func
        self.loop   = None
        self.thread = None

    def __get__(self, instance, owner):
        @wraps(self.func)
        def async_wrapper(*args, **kwargs):
            if self.loop is None:
                self.loop   = asyncio.new_event_loop()
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
            return asyncio.run_coroutine_threadsafe(self._async(instance, *args, **kwargs), self.loop)

        @wraps(self.func)
        def sync_wrapper(*args, **kwargs):
            return self.func(instance, *args, **kwargs)

        async_wrapper.sync  = sync_wrapper
        return async_wrapper

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _async(self, instance, *args, **kwargs):
        try:
            await self.loop.run_in_executor(None, lambda: self.func(instance, *args, **kwargs))
        except BaseException as e:
            trace(e)