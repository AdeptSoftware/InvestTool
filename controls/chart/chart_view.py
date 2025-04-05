# chart_view.py
from controls.abstract.source   import AbstractSource, SubscriptionType
from controls.abstract.renderer import AbstractDynamicRenderer
from controls.abstract.view     import AbstractView


class ChartView(AbstractView):
    """ Класс графика """
    def __init__(self, parent, source: AbstractSource, renderer: AbstractDynamicRenderer):
        assert (renderer is not None)
        assert (source   is not None)
        self._parent    = parent
        self._source    = source                                                                                        # type: AbstractSource
        super().__init__(renderer)
        renderer.P_DEFAULT_ZOOM_Y = 3

    def load(self, target, **kwargs):
        """ В зависимости от self._source производит инициализацию графика данными """
        if self._target:
            self._source.detach(self, SubscriptionType.CANDLE)

        self._data      = self._source.upload_candles(**kwargs)
        self._target    = target
        self._source.attach(self, SubscriptionType.CANDLE, **kwargs["__attach"])
        self.reset()

    def set_renderer(self, renderer):
        """ Позволяет установить тип отрисовщика """
        assert(renderer is not None)
        self._renderer  = renderer                                                                                       # !!! Добавить копирование настроек

    def update(self, item):
        """ Обновление содержимого графика """
        if self._data:
            self._data.update(item)
            self._parent.update()

