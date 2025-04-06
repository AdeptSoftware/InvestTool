# context.py
from PyQt5.QtGui                import QPainter, QPixmap, QFont, QFontMetrics
from PyQt5.QtGui                import QColor, QBrush, QPen
from PyQt5.QtCore               import Qt
from controls.abstract.context  import AbstractContext
from controls.wrapper.color     import Color
from controls.wrapper.point     import Point
from controls.wrapper.rect      import Rect
from typing                     import overload

class QtContext(AbstractContext):
    def __init__(self, parent):
        self._pixmap    = QPixmap(parent.width(), parent.width())
        self._parent    = parent
        self._font      = None                                                                                          # type: QFont
        self._painter   = None                                                                                          # type: QPainter
        self._metrics   = None                                                                                          # type: QFontMetrics

    @staticmethod
    def create_color(r, g, b) -> Color:
        return Color(r, g, b)

    def create_pen(self, *args, **kwargs):
        if 1 <= len(args) <= 2:
            return QPen(*args)
        elif 3 <= len(args) <= 4:
            width = (len(args) == 4 and args[3]) or 1
            return QPen(QColor(args[0], args[1], args[2]), width)
        else:
            TypeError("Invalid arguments for create_pen")

    def create_brush(self, *args, **kwargs):
        if len(args) == 1:
            if args[0] is None:
                return Qt.NoBrush
            return QBrush(*args)
        elif len(args) == 3:
            return QBrush(QColor(*args))
        else:
            TypeError("Invalid arguments for create_pen")

    @staticmethod
    def create_point(x, y) -> Point:
        return Point(x, y)

    @staticmethod
    def create_rect(x, y, w, h) -> Rect:
        return Rect(x, y, w, h)

    def resize(self, width, height):
        self._pixmap.detach()
        self._pixmap = QPixmap(width, height)

    def begin(self):
        self._painter = QPainter(self._pixmap)
        self._painter.setRenderHint(QPainter.Antialiasing)
        self._painter.setFont(self._font)

    def end(self):
        self._painter.end()
        return self._pixmap

    def rect(self) -> Rect:
        return Rect(self._parent.rect())

    def set_font(self, family, size):
        self._font      = QFont(family, size)
        self._metrics   = QFontMetrics(self._font)

    def text_height(self):
        return self._metrics.height()

    def text_width(self, text):
        return self._metrics.horizontalAdvance(text)

    def set_brush(self, brush):
        self._painter.setBrush(brush)

    def set_pen(self, pen):
        self._painter.setPen(pen)

    def draw_rect(self, rect):
        self._painter.drawRect(rect)

    def draw_line(self, x1, y1, x2, y2):
        self._painter.drawLine(x1, y1, x2, y2)

    def draw_text(self, x, y, text):
        self._painter.drawText(x, y, text)