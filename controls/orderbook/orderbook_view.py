# orderbook_view.py
from controls.abstract.view import AbstractView

class OrderBookView(AbstractView):
    """ Класс стакана """
    def set_focused_item(self, index):
        self._renderer.focused_item = max(-1, index)