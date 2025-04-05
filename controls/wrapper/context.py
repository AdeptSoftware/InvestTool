# context.py
from PyQt5.QtGui                import QPainter, QPixmap, QFont, QFontMetrics
from PyQt5.QtGui                import QColor, QBrush, QPen
from PyQt5.QtCore               import Qt
from controls.abstract.context  import AbstractContext
from controls.wrapper.color     import Color
from controls.wrapper.point     import Point
from controls.wrapper.rect      import Rect

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

    @staticmethod
    def create_pen(color, width):
        return QPen(color, width)

    @staticmethod
    def create_brush(color):
        if color is None:
            return Qt.NoBrush
        return QBrush(color)

    @staticmethod
    def create_point(x, y) -> Point:
        return Point(x, y)

    @staticmethod
    def create_rect(x, y, width, height) -> Rect:
        return Rect(x, y, width, height)

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