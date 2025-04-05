# view.py                                                                                                               # надеюсь я правильно понимаю смысл View
from controls.abstract.renderer import AbstractDynamicRenderer, Rect
from controls.abstract.observer import AbstractObserver

class AbstractView(AbstractObserver):
    """
    Абстрактные методы:\n
    * update(self, item)
    * load(self, target, **kwargs)
    """
    def __init__(self, renderer: AbstractDynamicRenderer):
        self._renderer  = renderer                                                                                      # type: AbstractDynamicRenderer
        super().__init__()

    def resize(self, width, height):
        """ Изменение размера """
        self._renderer.resize(width, height)

    def reset(self):
        """ Сброс настроек """
        self._renderer.reset()

    def zoom(self, dx, dy):
        """ Масштабирование """
        self._renderer.zoom(dx, dy)

    def scroll(self, dx, dy):
        """ Прокрутка """
        self._renderer.scroll(dx, dy)

    def render(self):
        """ Рендер """
        if self._data:
            self._renderer.set(self._data.const())
            return self._renderer.render()
        return None

    def coordinates(self) -> (str, Rect):
        """ Координаты элементов """
        for item in self._renderer.coordinates():
            yield item