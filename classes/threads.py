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


class BackgroundTask(BackgroundThread):
    """
    Класс, запускающий асинхронную функцию в отдельном потоке
    * async def _task(self)
    """
    def __init__(self):
        super().__init__()
        self._loop      = None                                                                                          # type: asyncio.AbstractEventLoop
        self._started   = threading.Event()

    def start(self, timeout=5):
        if super().start():
            self._started.wait(timeout=timeout)
            return True
        return False

    async def _task(self):
        pass

    def _main(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.create_task(self._task())
            self._started.set()
            self._loop.run_forever()
        except Exception:
            print(traceback.format_exc())
        finally:
            self._loop.close()

    def shutdown(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            while self._loop.is_running():
                time.sleep(0.01)
        super().shutdown()