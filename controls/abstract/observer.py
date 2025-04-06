# observer.py

class AbstractObserver:
    """
    Абстрактный класс наблюдателя, следящий за изменением данных\n
    * update(self, item=None)
    * load(self, target, **kwargs)
    """
    def __init__(self, target=None):
        self._target = target
        self._data   = None

    def target(self):
        """ Отслеживаемый объект """
        return self._target

    def load(self, target, **kwargs):
        """ Загрузка данных, сохранение target """
        pass

    def update(self, item=None):
        """ Произошло обновление данных """
        pass