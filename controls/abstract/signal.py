# signal.py

class AbstractSignal:
    def connect(self, callback):
        pass

    def notify(self, *args, **kwargs):
        pass