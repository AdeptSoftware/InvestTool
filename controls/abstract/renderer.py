# renderer.py
from controls.abstract.element  import AbstractRendererElement
from controls.abstract.context  import AbstractContext
from controls.abstract.layout   import AbstractLayout
from controls.abstract.model    import AbstractModel
from controls.utils.limits      import Limits
from typing                     import List, TypeVar, Generic, Optional, Type
from copy                       import copy

M = TypeVar('M', bound=AbstractModel)
L = TypeVar('L', bound=AbstractLayout)

class AbstractStaticRenderer(Generic[L]):
    """
    Класс статического отрисовщика\n
    * get_element(self, x, y) -> (int, AbstractRendererElement)
    """
    def __init__(self, ctx: AbstractContext):
        self._context = ctx
        self._layouts = []                                                                                              # type: List[AbstractLayout]

    def __getitem__(self, _type: Type[L]) -> Optional[L]:
        for layout in self._layouts:
            if type(layout) is _type:
                return layout
        return None

    def resize(self, width, height):
        self._context.resize(width, height)

    def render(self):
        self._context.begin()
        for layout in self._layouts:
            if layout.visible:
                layout.render(self)
        return self._context.end()

    @property
    def context(self):
        return self._context

    def get_element(self, x, y) -> (int, AbstractRendererElement):
        pass


class AbstractDynamicRenderer(AbstractStaticRenderer, Generic[M]):
    """
    Класс динамического отрисовщика (масштабирование, прокрутка)\n
    * get_element(self, x, y) -> (int, AbstractRendererElement)
    * prepare(self)
    """
    def __init__(self, ctx: AbstractContext, model: M):
        self._zoom      = Limits(0, 0)
        self._scroll    = Limits(0, 0)
        self._model     = model
        super().__init__(ctx)

    @property
    def zoom(self) -> Limits:
        return copy(self._zoom)

    @zoom.setter
    def zoom(self, value: Limits):
        assert(type(value) is Limits)
        self._zoom = value

    @property
    def scroll(self) -> Limits:
        return copy(self._scroll)

    @scroll.setter
    def scroll(self, value: Limits):
        assert(type(value) is Limits)
        self._scroll = value

    @property
    def model(self) -> M:
        return self._model

    @model.setter
    def model(self, value: M):
        self._model = value

    def reset(self):
        self._scroll.reset()
        self._zoom.reset()

    def resize(self, width, height):
        super().resize(width, height)

    def prepare(self):
        """ Этот метод нужен для подготовки элементов рендера """
        pass