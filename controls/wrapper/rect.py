# rect.py
from controls.abstract.context  import Rect     as _ARect
from PyQt5.QtCore               import QRect    as _QRect

class Rect(_QRect, _ARect):
    @property
    def left(self):
        return super().left()

    @property
    def top(self):
        return super().top()

    @property
    def right(self):
        return super().right()

    @property
    def bottom(self):
        return super().bottom()

    @property
    def width(self):
        return super().width()

    @property
    def height(self):
        return super().height()

    @left.setter
    def left(self, value):
        super().moveLeft(value)

    @top.setter
    def top(self, value):
        super().moveTop(value)

    @right.setter
    def right(self, value):
        super().moveRight(value)

    @bottom.setter
    def bottom(self, value):
        super().moveBottom(value)

    @width.setter
    def width(self, value):
        super().setWidth(value)

    @height.setter
    def height(self, value):
        super().setHeight(value)

    def adjusted(self, x1, y1, x2, y2) -> "Rect":
        return Rect(super().adjusted(x1, y1, x2, y2))

    def contain(self, x, y):
        return super().contains(x, y)

    def intersect(self, rect):
        return super().intersects(rect)

    def __copy__(self):
        return Rect(*super().getRect())