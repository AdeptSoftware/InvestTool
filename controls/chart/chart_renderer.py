# chart_renderer.py
import datetime

from controls.abstract.renderer         import AbstractDynamicRenderer, Limits
from controls.abstract.context          import AbstractContext

from controls.chart.layout.background   import BackgroundLayout
from controls.chart.layout.grid         import GridLayout
from controls.chart.layout.candlestick  import CandlestickLayout

import math
import sys

class ChartRenderer(AbstractDynamicRenderer):
    def __init__(self, ctx: AbstractContext):
        self.RENDERER_BORDER_WIDTH   = 5
        self.RENDERER_TEXT_GAP       = 3
        self.RENDERER_EQUAL_MODIFIER = 0.05
        ctx.set_font("Arial", 10)
        super().__init__(ctx)

        self._layouts += [
            BackgroundLayout(ctx),
            GridLayout(ctx),
            CandlestickLayout(ctx)
        ]
        self[GridLayout].index2str = lambda x: x.strftime("%H:%M")

    def coordinates(self):
        for candle in self[CandlestickLayout].candles:
            yield str(candle["item"]), candle["body"]

    def update(self, items):
        """ Обновление дескрипторов и слоев """
        rect   = self._context.rect()
        item_width    = self[CandlestickLayout].CANDLE_WIDTH + self._zoom.x
        element_width = item_width + self[CandlestickLayout].CANDLE_GAP
        # Предварительно определим набор данных
        first  = max(1, 1 + math.floor(self._scroll.x / element_width))
        width  = rect.width - (self.RENDERER_BORDER_WIDTH * 2) - self.RENDERER_TEXT_GAP
        last   = min(len(items), first + math.ceil(width / element_width))
        _items = items[-first:-last:-1]
        c_max  = _items.max_text_width(self._context)
        z_size = self._context.text_width('0')
        # Уточним набор данных
        width -= c_max + z_size
        last   = min(len(items), first + math.ceil(width / element_width))
        _items = items[-first:-last:-1]
        c_max  = _items.max_text_width(self._context) + z_size
        # Область отрисовки графика с учетом отступов
        rect   = rect.adjusted(
            self.RENDERER_BORDER_WIDTH,
            self.RENDERER_BORDER_WIDTH,
            -2 * self.RENDERER_BORDER_WIDTH - self.RENDERER_TEXT_GAP - c_max,
            -2 * self.RENDERER_BORDER_WIDTH - self.RENDERER_TEXT_GAP - self._context.text_height()
        )
        # Настроим диапазон значений
        y_min, y_max  = _items.bounds()
        if y_min == y_max:
            y_min *= 1 - self.RENDERER_EQUAL_MODIFIER
            y_max *= 1 + self.RENDERER_EQUAL_MODIFIER
        offset = self._zoom.y * ((y_max - y_min) / 20)
        y_min -= offset
        y_max += offset
        y_min, y_max, count = self._correct_bounds(rect, y_min, y_max)
        # Обновим данные слоёв
        self[GridLayout].set_vertical_lines(_items, element_width, rect)
        self[GridLayout].set_horizontal_lines(y_min, y_max, count, rect)
        self[CandlestickLayout].set_candles(_items, item_width, rect, y_min, y_max)
        # Обновим данные о граничных условиях масштабирования и перемешения
        x_min        = 1 - self[CandlestickLayout].CANDLE_WIDTH
        x_max        = rect.width // self[GridLayout].TICK_INTERVAL
        self._zoom   = Limits(x=self._zoom.x,   y=self._zoom.y,   x_min=x_min, x_max=x_max,       y_min=0, y_max=50)
        self._scroll = Limits(x=self._scroll.x, y=self._scroll.y, x_min=0,     x_max=sys.maxsize, y_min=0, y_max=0)

    def _correct_bounds(self, rect, y_min, y_max):
        """ Определяет количество линий по оси Y и их диапазон"""
        _diff = y_max - y_min
        _base = math.pow(10, math.floor(math.log10(_diff)))
        _min = _base * (y_min // _base)
        _max = _base * ((y_max // _base) + 1)

        if (_max - y_max) / _base > 0.5:
            _max -= _base * 0.5
        if (y_min - _min) / _base > 0.5:
            _min += _base * 0.5

        _cnt = 1
        delta = math.ceil((_max - _min) / (_base / 10))
        for _cnt in range(rect.height // (self._context.text_height() + self.RENDERER_TEXT_GAP), 1, -1):
            if delta % _cnt == 0:
                break

        return _min, _max, _cnt