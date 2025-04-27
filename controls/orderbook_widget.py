# orderbook_widget.py
from controls.orderbook.orderbook_view      import OrderbookView
from controls.orderbook.orderbook_renderer  import OrderBookRenderer

from controls.wrapper.widget                import Widget
from controls.wrapper.context               import QtContext

from PyQt5.QtWidgets                        import QWidget, QMenu

class OrderBookWidget(Widget):
    """ Класс виджета стопки """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.view = OrderbookView(self, OrderBookRenderer(QtContext(self)))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._captured_position is None:
            x = event.pos().x()
            y = event.pos().y()
            index, item = self.view.get_element(x, y)
            if item and item.rect.top <= y <= item.rect.bottom:
                self.view.set_focused_item(index)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.view.set_focused_item(-1)

    def contextMenuEvent(self, event):
        menu    = QMenu()
        action1 = menu.addAction("Сбросить")
        action1.triggered.connect(self.view.reset)
        menu.exec(event.globalPos())