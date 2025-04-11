# event_method.py
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
    def __init__(self, func):
        self.func   = func
        self.name   = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if not hasattr(instance, "_event_subscribers_"):
            instance._event_subscribers_ = {}
            instance._event_methods_     = {}

        if self.name not in instance._event_subscribers_:
            instance._event_subscribers_[self.name] = []
            instance._event_methods_[self.name]     = None

            @wraps(self.func)
            def method_wrapper(*args, **kwargs):
                result = self.func(instance, *args, **kwargs)
                call()
                return result

            def subscribe(callback):
                if callback not in instance._event_subscribers_[self.name]:
                    instance._event_subscribers_[self.name].append(callback)

            def unsubscribe(callback):
                if callback in instance._event_subscribers_[self.name]:
                    instance._event_subscribers_[self.name].remove(callback)

            def call():
                for func in instance._event_subscribers_[self.name]:
                    func()

            method_wrapper.call         = call
            method_wrapper.subscribe    = subscribe
            method_wrapper.unsubscribe  = unsubscribe
            instance._event_methods_[self.name] = method_wrapper

        return instance._event_methods_[self.name]