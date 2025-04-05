# orderbook_widget.py
from controls.orderbook.orderbook_view      import OrderBookView
from controls.orderbook.orderbook_renderer  import OrderBookRenderer
from controls.abstract.source               import AbstractSource

from controls.wrapper.widget                import AdeptWidget
from controls.wrapper.context               import QtContext

from PyQt5.QtWidgets                        import QMenu

class OrderBookWidget(AdeptWidget):
    """ Класс виджета стопки """

    def __init__(self, parent, source: AbstractSource):
        """
        Конструктор класса виджета графика
        :param parent: родительское окно
        :param source: источник данных
        """
        super().__init__(parent)
        self.view = OrderBookView(self, source, OrderBookRenderer(QtContext(self)))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._captured_position is None:
            index = 0
            y     = event.pos().y()
            for _, rect in self.view.coordinates():
                if rect.top <= y <= rect.bottom:
                    self.view.set_focused_item(index)
                    self.update()
                    return
                index += 1

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.view.set_focused_item(-1)
        self.update()

    def contextMenuEvent(self, event):
        menu    = QMenu()
        action1 = menu.addAction("Сбросить")
        action1.triggered.connect(self.view.reset)
        menu.exec(event.globalPos())