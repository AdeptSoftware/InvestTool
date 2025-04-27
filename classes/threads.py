# threads.py
import threading
import time
import traceback
import asyncio

class BackgroundThread:
    """
    Класс, запускающий код в отдельном потоке
    * def _main(self)
    """
    def __init__(self):
        self._thread = None                                                                                             # type: threading.Thread

    def start(self):
        if self._thread and self._thread.is_alive():
            return False

        self._thread = threading.Thread(target=self._main, daemon=True)
        self._thread.start()
        return True

    def shutdown(self):
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def _main(self):
        pass


class BackgroundLoop:
    """
    Класс, запускающий асинхронную функцию в текущем потоке
    * async def _task(self)
    """
    def __init__(self):
        self._loop      = None                                                                                          # type: asyncio.AbstractEventLoop
        self._started   = threading.Event()

    def start(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

            try:
                self._loop.create_task(self._task())
                self._started.set()
                self._loop.run_forever()
            except Exception:
                print(traceback.format_exc())
                self._loop.close()

    def shutdown(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            while self._loop.is_running():
                time.sleep(0.01)
            self._started.clear()
            self._loop = None

    async def _task(self):
        pass


class BackgroundTask(BackgroundThread, BackgroundLoop):
    """
    Класс, запускающий асинхронную функцию в отдельном потоке
    * async def _task(self)
    """
    def __init__(self):
        BackgroundThread.__init__(self)
        BackgroundLoop.__init__(self)

    def start(self, timeout=5):
        if BackgroundThread.start(self):
            self._started.wait(timeout=timeout)
            return True
        return False

    def _main(self):
        BackgroundLoop.start(self)

    def shutdown(self):
        BackgroundLoop.shutdown(self)
        BackgroundThread.shutdown(self)

