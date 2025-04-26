# t_lazy_call.py
from tinkoff.invest import Client

class LazyCall:
    def __init__(self, token, pointer):
        self._pointer = pointer
        self._token   = token

    @property
    def __name__(self):
        return str(self._pointer)

    def __call__(self, *args, **kwargs):
        with Client(self._token) as client:
            method = self._pointer(client)
            return method(*args, **kwargs)