# background_task.py
from threading      import Thread, Event, RLock
from classes.trace  import trace

class BackgroundTask:
    def __init__(self):
        self._stop_event = Event()
        self._lock       = RLock()
        self._thread     = None

    def _run(self):
        pass

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._thread = Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1)
            self._thread = None