# view.py                                                                                                               # надеюсь я правильно понимаю смысл View
from controls.abstract.renderer import AbstractDynamicRenderer, AbstractRendererElement, Limits
from controls.abstract.widget   import AbstractWidget
from controls.abstract.model    import AbstractModel
from controls.utils.event       import EventMethod
from typing                     import TypeVar, Generic, Type

T = TypeVar('T', bound=AbstractModel)

class BaseView(Generic[T]):
    """ Базовый класс представления данных """
    def __init__(self, parent: AbstractWidget, renderer: AbstractDynamicRenderer[T]):
        self._renderer = renderer
        self._parent   = parent

    @EventMethod
    def prepare(self):
        """ Подготовка содержимого к отрисовке """
        self._renderer.prepare()

    def render(self):
        """ Отрисовка содержимого, но без обновления экрана """
        return self._renderer.render()

    def invalidate(self):
        """ Подготовка и отрисовка содержимого и обновление экрана """
        self.prepare()
        self._parent.update()                                                                                           # Внутри вызывается view.render()

    @property
    def model(self) -> T:
        return self._renderer.model

    @model.setter
    def model(self, value : T):
        self._renderer.model = value
        self.invalidate()

    def resize(self, width, height):
        self._renderer.resize(width, height)
        self.invalidate()

    def reset(self):
        self._renderer.reset()
        self.invalidate()

    @property
    def zoom(self):
        return self._renderer.zoom

    @zoom.setter
    def zoom(self, value: Limits):
        self._renderer.zoom = value
        self.invalidate()

    @property
    def scroll(self):
        return self._renderer.scroll

    @scroll.setter
    def scroll(self, value: Limits):
        self._renderer.scroll = value
        self.invalidate()

    def get_element(self, x, y) -> (int, AbstractRendererElement):
        return self._renderer.get_element(x, y)