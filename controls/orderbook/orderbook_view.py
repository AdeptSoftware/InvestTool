# orderbook_view.py
from controls.abstract.widget               import AbstractWidget
from controls.abstract.view                 import AbstractView
from controls.abstract.source               import AbstractSource
from controls.orderbook.orderbook_renderer  import OrderBookRenderer


class OrderbookView(AbstractView[AbstractSource]):
    def __init__(self, parent: AbstractWidget, renderer: OrderBookRenderer):
        super().__init__(parent, renderer)

    def update(self):
        self._renderer.update()
        self._parent.update()

    def set_focused_item(self, index):
        self._renderer.set_focused_item(index)