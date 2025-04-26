# event.py
import asyncio
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
x.update.connect(some_func1)                # some_func1(data) - подписываемая функция

y = B()
y.update.connect(some_func2)                # some_func2(data) - подписываемая функция

"""


class EventMethod:
    """ Создает обернутый метод, при вызове которого происходит уведомление всех подписавшихся """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if not hasattr(instance, "_event_subscribers_"):
            instance._event_subscribers_ = {}
            instance._event_methods_   = {}

        if self.func.__name__ not in instance._event_subscribers_:
            instance._event_subscribers_[self.func.__name__] = []
            instance._event_methods_[self.func.__name__]     = None

            def connect(callback):
                if callback and callback not in instance._event_subscribers_[self.func.__name__]:
                    instance._event_subscribers_[self.func.__name__].append(callback)

            def disconnect(callback):
                if callback and callback in instance._event_subscribers_[self.func.__name__]:
                    instance._event_subscribers_[self.func.__name__].remove(callback)

            ### sync ###

            @wraps(self.func)
            def sync_wrapper(*args, **kwargs):
                result = self.func(instance, *args, **kwargs)
                sync_notify()
                return result

            def sync_notify():
                for callback in instance._event_subscribers_[self.func.__name__]:
                    callback()

            ### async ###

            @wraps(self.func)
            async def async_wrapper(*args, **kwargs):
                result = await self.func(instance, *args, **kwargs)
                await async_notify()
                return result

            async def async_notify():
                for callback in instance._event_subscribers_[self.func.__name__]:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        raise TypeError(f"Isn't coroutine: {str(callback)}")

            ### обертка ###

            is_async                  = asyncio.iscoroutinefunction(self.func)
            method_wrapper            = async_wrapper if is_async else sync_wrapper
            method_wrapper.notify     = async_notify  if is_async else sync_notify
            method_wrapper.connect    = connect
            method_wrapper.disconnect = disconnect
            instance._event_methods_[self.func.__name__] = method_wrapper

        return instance._event_methods_[self.func.__name__]