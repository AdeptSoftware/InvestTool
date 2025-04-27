# candlestick.py
from controls.abstract.context import AbstractContext
from controls.abstract.layout  import AbstractLayout
from controls.utils.functions  import interpolate
from typing                    import List

class CandlestickLayout(AbstractLayout):
    """ Слой свечного графика """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.CANDLE_GAP         = 3
        self.CANDLE_WIDTH       = 12
        self.WICK_WIDTH         = 1

        self.CANDLE_UP_PEN      = ctx.create_pen  ( 38, 185, 107)
        self.CANDLE_UP_BRUSH    = ctx.create_brush(  6, 170,  84)
        self.CANDLE_DOWN_BRUSH  = ctx.create_brush(210,  52,  43)
        self.CANDLE_DOWN_PEN    = ctx.create_pen  (216,  73,  67)
        self.CANDLE_FOCUSED     = ctx.create_pen  (255, 255,   0, width=4)

        self._candles           = []
        self._focused_index     = -1

    @property
    def candles(self):
        return self._candles

    def set_focused_item(self, index):
        self._focused_index = max(-1, min(index, len(self._candles)))

    def set_candles(self, items, width, rect, y_min, y_max):
        """
        Вычисление прямоугольных областей свечей
        :param items:  данные типа AbstractData
        :param width:  ширина одного item (с учетом масштаба и self.CANDLE_WIDTH) без self.CANDLE_GAP
        :param rect:   область отрисовки данных
        :param y_min:  минимальное значение по оси Y
        :param y_max:  максимальное значение по оси Y
        """
        candles  = []
        x        = rect.right - (width // 2)
        coord    = (rect.bottom, rect.top)
        for item in items:
            _min = round(interpolate(coord[0], coord[1], y_min, y_max, min(item.open,  item.close)))
            _max = round(interpolate(coord[0], coord[1], y_min, y_max, max(item.close, item.open)))
            y1   = round(interpolate(coord[0], coord[1], y_min, y_max, item.high))
            y0   = round(interpolate(coord[0], coord[1], y_min, y_max, item.low))

            candles += [{
                "body":     self._context.create_rect(x=x-(width//2),           y=_min, w=width,           h=_max-_min),
                "wick":     self._context.create_rect(x=x-(self.WICK_WIDTH//2), y=y0,   w=self.WICK_WIDTH, h=y1-y0),
                "down":     item.close < item.open,
                "item":     item
            }]
            x -= width + self.CANDLE_GAP
        self._candles = candles

    def render(self, renderer):
        for index, candle in enumerate(self._candles):
            if candle["down"]:
                self._context.set_brush(self.CANDLE_DOWN_BRUSH)
                self._context.set_pen(self.CANDLE_DOWN_PEN)
            else:
                self._context.set_brush(self.CANDLE_UP_BRUSH)
                self._context.set_pen(self.CANDLE_UP_PEN)
            if self._focused_index == index:
                self._context.set_pen(self.CANDLE_FOCUSED)
            self._context.draw_rect(candle["wick"])
            self._context.draw_rect(candle["body"])