# widget.py
from PyQt5.QtWidgets                        import QWidget
from PyQt5.QtGui                            import QPainter, QWheelEvent, QKeyEvent, QShowEvent, QPixmap
from PyQt5.QtCore                           import Qt, QPoint, QTimer

from controls.abstract.view                 import BaseView
from controls.abstract.widget               import AbstractWidget
from controls.wrapper.signal                import Signal, pyqtSignal


class Widget(QWidget, AbstractWidget):
    """ Класс, реализующий базовые функции навигации и отрисовки графика """
    __signal = pyqtSignal()

    def __init__(self, parent: QWidget):
        """
        Конструктор класса виджета графика
        :param parent: родительское окно
        """
        QWidget.__init__(self, parent)
        self.view               = None                                                                                  # type: BaseView
        self._captured_position = None                                                                                  # type: QPoint

        self.update_signal      = Signal(self.__signal, self.prepare)
        self.update_signal.connect(self.update)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    # Логика перетаскивания содержимого

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._captured_position = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._captured_position = None

    def mouseMoveEvent(self, event):
        if self._captured_position is not None:
            offset = event.pos() - self._captured_position
            self._captured_position = event.pos()
            self.scroll(offset.x(), offset.y())

    # Логика масштабирования содержимого

    def _zoom(self, event, condition, mult=1):
        factor = (1 + 2*(-1*int(condition))) * mult
        if event.modifiers() & Qt.ShiftModifier:
            self.view.zoom = self.view.zoom(0, factor)
        else:
            self.view.zoom = self.view.zoom(factor, 0)

    def wheelEvent(self, event : QWheelEvent):
        self._zoom(event, event.angleDelta().y() < 0)

    def keyPressEvent(self, event : QKeyEvent):
        key = event.key()
        if key in [Qt.Key_Plus, Qt.Key_Minus]:
           self._zoom(event, key == Qt.Key_Minus, 5)
        elif key in [Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right]:
            x = -1 if key == Qt.Key_Right else 1 if key == Qt.Key_Left else 0
            y = -1 if key == Qt.Key_Down  else 1 if key == Qt.Key_Up   else 0
            self.view.scroll = self.view.scroll(x * 20, y * 20)

    # Логика отрисовки изображений

    def paintEvent(self, event):
        pixmap : QPixmap = self.view.render()
        if pixmap is not None:
            painter = QPainter(self)
            painter.drawPixmap(pixmap.rect(), pixmap)
            painter.end()

    # Прочее

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        self.view.resize(self.width(), self.height())

    def showEvent(self, event: QShowEvent):
        if QWidget.isVisible(self):
            self.view.invalidate()
        super().showEvent(event)

    def visible(self) -> bool:
        return QWidget.isVisible(self)

    def prepare(self):
        self.view.prepare()

    def scroll(self, dx, dy):
        self.view.scroll = self.view.scroll(dx, dy)