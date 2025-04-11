# renderer.py
from controls.abstract.source   import AbstractSource
from controls.abstract.context  import AbstractContext
from controls.abstract.layout   import AbstractLayout
from controls.utils.limits      import Limits
from typing                     import List, TypeVar, Generic, Type, Optional

T = TypeVar('T')

class AbstractStaticRenderer(Generic[T]):
    """
    Класс статического отрисовщика\n
    * coordinates(self)
    * update(self, source: AbstractDataSource)
    """
    def __init__(self, ctx: AbstractContext):
        self._context = ctx
        self._layouts = []                                                                                              # type: List[AbstractLayout]

    def __getitem__(self, _type: Type[T]) -> Optional[T]:
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
                layout.render()
        return self._context.end()

    def coordinates(self):
        """ Координаты основных элементов """
        pass

    def update(self, source: AbstractSource):
        """ Обновление дескрипторов и слоев """
        pass


class AbstractDynamicRenderer(AbstractStaticRenderer):
    """
    Класс динамического отрисовщика (масштабирование, прокрутка)\n
    * coordinates(self)
    * update(self, source: AbstractDataSource)
    """
    def __init__(self, ctx: AbstractContext):
        self._zoom   = Limits(0, 0)
        self._scroll = Limits(0, 0)
        super().__init__(ctx)

    def zoom(self, dx, dy):
        self._zoom(dx, dy)

    def scroll(self, dx, dy):
        self._scroll(dx, dy)

    def reset(self):
        self._scroll.reset()
        self._zoom.reset()