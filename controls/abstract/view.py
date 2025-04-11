# view.py                                                                                                               # надеюсь я правильно понимаю смысл View
from controls.abstract.renderer import AbstractDynamicRenderer
from controls.abstract.source   import AbstractSource
from controls.abstract.widget   import AbstractWidget

class AbstractView:
    def __init__(self, parent: AbstractWidget, renderer: AbstractDynamicRenderer):
        self._renderer  = renderer
        self._parent    = parent
        self._source    = None                                                                                          # type: AbstractSource

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source: AbstractSource):
        self._source = source

    def update(self):
        """ Обновление содержимого """
        if self._parent.visible():
            self._renderer.update(self._source)

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
        return self._renderer.render()

    def coordinates(self):
        """ Координаты элементов """
        for item in self._renderer.coordinates():
            yield item