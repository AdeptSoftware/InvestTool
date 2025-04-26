# view.py                                                                                                               # надеюсь я правильно понимаю смысл View
from controls.abstract.renderer import AbstractDynamicRenderer, AbstractRendererElement
from controls.abstract.widget   import AbstractWidget
from controls.abstract.model    import AbstractModel
from typing                     import TypeVar, Generic, Type

T = TypeVar('T', bound=AbstractModel)

class AbstractView(Generic[T]):
    """
    Абстрактный класс представления данных
    * async def update(self)
    """
    def __init__(self, parent : AbstractWidget, renderer: AbstractDynamicRenderer[T]):
        self._renderer = renderer
        self._parent   = parent

    def update(self):
        """ Обновление содержимого при изменении данных модели """
        pass

    @property
    def model(self) -> T:
        return self._renderer.model

    @model.setter
    def model(self, value : T):
        if self._renderer.model:
            self._renderer.model.update.disconnect(self._parent.update)
        self._renderer.model = value
        self._renderer.model.update.connect(self._parent.update)

    def resize(self, width, height):
        self._renderer.resize(width, height)

    def reset(self):
        self._renderer.reset()

    @property
    def zoom(self):
        return self._renderer.zoom

    @property
    def scroll(self):
        return self._renderer.scroll

    def render(self):
        return self._renderer.render()

    def get_element(self, x, y) -> (int, AbstractRendererElement):
        return self._renderer.get_element(x, y)