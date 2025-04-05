# color.py
from controls.abstract.context  import Color    as _AColor
from PyQt5.QtGui                import QColor   as _QColor

class Color(_QColor, _AColor):
    @property
    def r(self):
        return self.red()

    @property
    def g(self):
        return self.green()

    @property
    def b(self):
        return self.blue()

    @r.setter
    def r(self, value):
        self.setRed(value)

    @g.setter
    def g(self, value):
        self.setGreen(value)

    @b.setter
    def b(self, value):
        self.setBlue(value)

