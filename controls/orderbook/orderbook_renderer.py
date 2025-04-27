# orderbook_renderer.py
from controls.abstract.renderer          import AbstractDynamicRenderer, AbstractRendererElement, Limits
from controls.abstract.context           import AbstractContext
from controls.abstract.source            import AbstractSource

from controls.layout.background          import BackgroundLayout
from controls.orderbook.layout.orderbook import OrderBookLayout


class OrderBookRenderer(AbstractDynamicRenderer[AbstractSource]):
    def __init__(self, ctx : AbstractContext):
        self.P_DEFAULT_ZOOM_Y   = 2
        super().__init__(ctx, None)
        ctx.set_font(ctx.create_font("Arial", 10))

        self._layouts          += [
            BackgroundLayout(ctx),
            OrderBookLayout(ctx)
        ]

    def set_focused_item(self, index):
        self[OrderBookLayout].set_focused_item(index)

    def get_element(self, x, y) -> (int, AbstractRendererElement):
        with self[OrderBookLayout].lock:
            for index, item in enumerate(self[OrderBookLayout].items):
                if item.rect.contain(x, y):
                    return index, item
        return None, None

    def prepare(self):
        if self._model:
            self[OrderBookLayout].prepare(self._model.orderbook(), self._model.last_price(), self._scroll, self._zoom)
            self._zoom   = Limits(x=self._zoom.x,   y=self._zoom.y,   x_min=-100, x_max=20, y_min=0,    y_max=25)
            self._scroll = Limits(x=self._scroll.x, y=self._scroll.y, x_min=0,    x_max=0,
                                  y_min=self[OrderBookLayout].scroll_min, y_max=self[OrderBookLayout].scroll_max)
