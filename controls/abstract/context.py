# context.py
from typing import overload

class Point:
    @property
    def x(self):                                                                                                        # noqa
        pass

    @property
    def y(self):                                                                                                        # noqa
        pass

    @x.setter
    def x(self, value):
        pass

    @y.setter
    def y(self, value):
        pass


class Rect:
    @property
    def left(self):                                                                                                     # noqa
        pass

    @property
    def top(self):                                                                                                      # noqa
        pass

    @property
    def right(self):                                                                                                    # noqa
        pass

    @property
    def bottom(self):                                                                                                   # noqa
        pass

    @property
    def width(self):                                                                                                    # noqa
        pass

    @property
    def height(self):                                                                                                   # noqa
        pass


    @left.setter
    def left(self, value):
        pass

    @top.setter
    def top(self, value):
        pass

    @right.setter
    def right(self, value):
        pass

    @bottom.setter
    def bottom(self, value):
        pass

    @width.setter
    def width(self, value):
        pass

    @height.setter
    def height(self, value):
        pass

    def adjusted(self, x1, y1, x2, y2):
        pass

class Color:
    @property
    def r(self):                                                                                                        # noqa
        pass

    @property
    def g(self):                                                                                                        # noqa
        pass

    @property
    def b(self):                                                                                                        # noqa
        pass

    @r.setter
    def r(self, value):
        pass

    @g.setter
    def g(self, value):
        pass

    @b.setter
    def b(self, value):
        pass


class AbstractContext:
    """ Астрактный класс контекста рисования """
    @staticmethod
    def create_color(r, g, b) -> Color:
        pass

    @overload
    def create_pen(self, color, width=1): ...
    @overload
    def create_pen(self, r, g, b, width=1): ...

    def create_pen(self, *args, **kwargs):
        raise NotImplemented("Must be implemented in subclass")

    @overload
    def create_brush(self, color):
        """ Если передать color = None, то должен вернуть кисть без заливки """
        ...

    @overload
    def create_brush(self, r, g, b): ...

    def create_brush(self, *args, **kwargs):
        raise NotImplemented("Must be implemented in subclass")

    @staticmethod
    def create_point(x, y) -> Point:
        pass

    @staticmethod
    def create_rect(x, y, w, h) -> Rect:
        pass

    @staticmethod
    def create_font(family, size, bold=False, italic=False):
        pass

    def resize(self, width, height):
        pass

    def begin(self):
        pass

    def end(self):
        """ Должен возвращать объект, содержащий сгенерированное изображение """
        pass

    def rect(self) -> Rect:
        pass

    def set_font(self, font):
        pass

    def set_brush(self, brush):
        pass

    def set_pen(self, pen):
        pass

    def text_height(self):
        pass

    def text_width(self, text):
        pass

    def draw_rect(self, rect):
        pass

    def draw_line(self, x1, y1, x2, y2):
        pass

    def draw_text(self, x, y, text):
        pass

