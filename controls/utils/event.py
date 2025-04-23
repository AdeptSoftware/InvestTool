# event.py
from functools import wraps

"""
Пример:
class A:
    @EventMethod
    def update(self, value):
        print(str(value))

class B(A):
    @EventMethod
    def update(self, data):
        print(str(value))
#       super().update(value)               # Раскомментировав, произойдет повторный вызов подписанной функции 

x = A()
x.update.subscribe(some_func1)              # some_func1(data) - подписываемая функция

y = B()
y.update.subscribe(some_func2)              # some_func2(data) - подписываемая функция

"""


class EventMethod:
    """ Создает обернутый метод, при вызове которого происходит уведомление всех подписавшихся """
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        if not hasattr(instance, "_event_callbacks_"):
            instance._event_callbacks_ = {}
            instance._event_methods_   = {}

        if self.method.__name__ not in instance._event_callbacks_:
            instance._event_callbacks_[self.method.__name__] = []
            instance._event_methods_[self.method.__name__]   = None

            @wraps(self.method)
            def method_wrapper(*args, **kwargs):
                result = self.method(instance, *args, **kwargs)
                notify()
                return result

            def connect(callback):
                if callback and callback not in instance._event_callbacks_[self.method.__name__]:
                    instance._event_callbacks_[self.method.__name__].append(callback)

            def disconnect(callback):
                if callback and callback in instance._event_callbacks_[self.method.__name__]:
                    instance._event_callbacks_[self.method.__name__].remove(callback)

            def notify():
                for callback in instance._event_callbacks_[self.method.__name__]:
                    callback()

            method_wrapper.notify     = notify
            method_wrapper.connect    = connect
            method_wrapper.disconnect = disconnect
            instance._event_methods_[self.method.__name__] = method_wrapper

        return instance._event_methods_[self.method.__name__]