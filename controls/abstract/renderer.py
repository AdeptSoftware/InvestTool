# renderer.py
from controls.abstract.context  import AbstractContext, Rect
from dataclasses                import dataclass

@dataclass
class Limits:
    x_min:  int
    x_max:  int
    y_min:  int
    y_max:  int


class AbstractRenderer:
    """
    Абстрактный класс отрисовщика\n
    * coordinates(self) -> (str, Rect)
    * update(self)
    * set(self, data)
    * render(self)
    """
    def __init__(self, context : AbstractContext):
        self._context = context                                                                                         # type: AbstractContext

    def resize(self, width, height):
        self._context.resize(width, height)
        self.update()

    def coordinates(self) -> (str, Rect):
        """ Генератор, возвращающий координаты элементов графика """
        pass

    def update(self):
        """ Обновление данных отрисовщика """
        pass

    def set(self, data):
        """ Обработка входных данных перед рендером """
        pass

    def render(self):
        """
        Рендер данных
        :return: Возвращает объект, содержащий сгенерированное изображение (зависит от self._context)
        """
        pass



class AbstractDynamicRenderer(AbstractRenderer):
    """
    Абстрактный класс отрисовщика объекта, в котором можно изменять масштаб и перемещать отдельные элементы\n
    * см. у родительского класса
    """
    P_DEFAULT_ZOOM_Y = 0
    P_DEFAULT_ZOOM_X = 0

    def __init__(self, context : AbstractContext):
        super().__init__(context)
        self._scroll_limits = Limits(0, 0, 0, 0)
        self._zoom_limits   = Limits(0, self.P_DEFAULT_ZOOM_X, 0, self.P_DEFAULT_ZOOM_Y)
        self._zoom          = context.create_point(self.P_DEFAULT_ZOOM_X, self.P_DEFAULT_ZOOM_Y)
        self._scroll        = context.create_point(0, 0)

    def zoom(self, dx, dy):
        """ Изменение масштаба """
        self._zoom.x = max(min(self._zoom.x + dx, self._zoom_limits.x_max), self._zoom_limits.x_min)
        self._zoom.y = max(min(self._zoom.y + dy, self._zoom_limits.y_max), self._zoom_limits.y_min)

    def reset(self):
        """ Сброс настроек графика """
        self._scroll = self._context.create_point(0, 0)
        self._zoom   = self._context.create_point(self.P_DEFAULT_ZOOM_X, self.P_DEFAULT_ZOOM_Y)

    def scroll(self, dx, dy):
        """ Прокрутка """
        self._scroll.x = max(min(self._scroll.x + dx, self._scroll_limits.x_max), self._scroll_limits.x_min)
        self._scroll.y = max(min(self._scroll.y + dy, self._scroll_limits.y_max), self._scroll_limits.y_min)