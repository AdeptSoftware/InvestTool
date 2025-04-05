# point.py
from controls.abstract.context  import Point    as _APoint
from PyQt5.QtCore               import QPoint   as _QPoint

class Point(_QPoint, _APoint):
    @property
    def x(self):
        return super().x()

    @property
    def y(self):
        return super().y()

    @x.setter
    def x(self, value):
        super().setX(value)

    @y.setter
    def y(self, value):
        super().setY(value)
