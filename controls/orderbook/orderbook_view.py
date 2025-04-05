# orderbook_view.py
from controls.abstract.source               import AbstractSource, SubscriptionType
from controls.abstract.view                 import AbstractView
from controls.abstract.data                 import AbstractData
from controls.orderbook.orderbook_renderer  import OrderBookRenderer

class OrderBookView(AbstractView):
    """ Класс стакана """
    def __init__(self, parent, source: AbstractSource, renderer: OrderBookRenderer):
        """
        Конструктор класса виджета графика
        :param parent: родительское окно
        :param view:
        """
        super().__init__(renderer)
        self._parent    = parent
        self._source    = source                                                                                        # type: AbstractSource

    def set_focused_item(self, index):
        self._renderer.focused_item = max(-1, index)

    def update(self, data):
        """ Произошло обновление данных """
        if issubclass(data.__class__, AbstractData):
            data.last_price = self._data.last_price
            self._data = data
            self._parent.update()
        else:
            self._data.last_price = data

    def load(self, target, **kwargs):
        """ Загрузка данных, сохранение target """
        if self._target:
            self._source.detach(self, SubscriptionType.ORDERBOOK)
            self._source.detach(self, SubscriptionType.LAST_PRICE)

        self._data = self._source.upload_orderbook(**kwargs)
        self._target = target
        self._source.attach(self, SubscriptionType.ORDERBOOK, depth=kwargs["depth"])
        self._source.attach(self, SubscriptionType.LAST_PRICE)
        self.reset()