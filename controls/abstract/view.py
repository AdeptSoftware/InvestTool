# view.py                                                                                                               # надеюсь я правильно понимаю смысл View
from controls.abstract.renderer import AbstractDynamicRenderer
from controls.abstract.observer import AbstractObserver

class AbstractView(AbstractObserver):
    """
    Абстрактные методы:\n
    * update(self, item=None)
    * load(self, target, **kwargs)
    """
    def __init__(self, renderer: AbstractDynamicRenderer):
        self._renderer  = renderer                                                                                      # type: AbstractDynamicRenderer
        super().__init__()

    def resize(self, width, height):
        """ Изменение размера """
        self._renderer.resize(width, height)
        self.update()

    def reset(self):
        """ Сброс настроек """
        self._renderer.reset()
        self.update()

    def zoom(self, dx, dy):
        """ Масштабирование """
        self._renderer.zoom(dx, dy)
        self.update()

    def scroll(self, dx, dy):
        """ Прокрутка """
        self._renderer.scroll(dx, dy)
        self.update()

    def render(self):
        """ Рендер """
        return self._renderer.render()

    def coordinates(self):
        """ Координаты элементов """
        for item in self._renderer.coordinates():
            yield item