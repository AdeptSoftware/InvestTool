# orderbook_renderer.py
from controls.abstract.renderer import AbstractDynamicRenderer, Limits
from controls.abstract.context  import AbstractContext, Rect, Color
from dataclasses                import dataclass
from enum                       import Enum
import math

class OrderType(Enum):
    ASK = 0
    BID = 1
    SEP = 2

@dataclass
class _OrderBookRendererItem:
    text:       str                 # текст
    rect:       Rect                # прямоугольная область всего элемента
    x_rect:     Rect                # прямоугольная область закрашенной части
    focused:    bool                # элемент в фокусе
    type:       OrderType           # тип элемента

class OrderBookRenderer(AbstractDynamicRenderer):
    def __init__(self, ctx : AbstractContext):
        self.P_DEFAULT_ZOOM_Y   = 2
        super().__init__(ctx)
        ctx.set_font("Arial", 10)

        self.P_GAP_HEIGHT       = 0
        self.P_BORDER_WIDTH     = 1
        self.P_TEXT_OFFSET      = 10
        self.P_ITEM_HEIGHT      = 20
        self.P_BORDER_COLOR     = ctx.create_color( 44,  44,  44)
        self.P_BACKGROUND_COLOR = ctx.create_color( 28,  28,  28)
        self.P_FOCUS_COLOR      = ctx.create_color(  0,   0,   0)
        self.P_SEPARATOR_COLOR  = ctx.create_color(  0,   0,   0)
        self.P_SELL_COLOR       = ctx.create_color(255,   0,   0)
        self.P_BUY_COLOR        = ctx.create_color(  0, 255,   0)
        self.P_TEXT_COLOR       = ctx.create_color(  0, 102, 204)

        self._item_height       = None

        self.focused_item       = -1

        self._items             = []                                                                                    # type: list[_OrderBookRendererItem]
        self._rect              = None                                                                                  # type: Rect
        self._max_scroll        = None
        self._center            = 0

    def coordinates(self) -> (str, Rect):
        for item in self._items:
            yield str(item), item.rect

    def update(self, items):
        self._set(items)

    def _update(self, items):
        self._rect                  = self._context.rect()
        self._item_height           = self.P_ITEM_HEIGHT + self._zoom.y
        element_height              = self._item_height + self.P_GAP_HEIGHT

        visible_count               = math.floor(self._rect.height / element_height)
        total                       = (items and len(items)) or 0
        self._max_scroll            = (max(0, total - visible_count) * element_height)

        _min                        = 0
        _max                        = 0
        if items:
            index = 0
            for item in items:
                index += 1
                if item.type == OrderType.SEP:
                    break
            half                    = math.floor(element_height / 2)
            center                  = math.floor(element_height * (index - 0.5))
            self._center            = center - math.floor(self._rect.height / 2)
            _max                    = self._center + self.P_BORDER_WIDTH
            _min                   -= (self._max_scroll - self._center) - half
        #   print(f"y={self._scroll.y}, center={self._center}, min={_min}, max={_max} -> {items[0]}, {items[-1]}")

        self._zoom   = Limits(x=self._zoom.x,   y=self._zoom.y,   x_min=-100, x_max=20, y_min=0,    y_max=25)
        self._scroll = Limits(x=self._scroll.x, y=self._scroll.y, x_min=0,    x_max=0,  y_min=_min, y_max=_max)

    def _set(self, data):
        assert (data is not None)
        assert (len(data) != 0)
        self._update(data)
        # Определим некоторые вспомогательные данные
        max_count   = 1
        ask_count   = 0
        bid_count   = 0
        sum_count   = 0
        for item in data:
            max_count = max(item.count, max_count)
            match item.type:
                case OrderType.ASK:
                    ask_count += item.count
                case OrderType.BID:
                    bid_count += item.count
            sum_count += item.count
        sum_count = max(1, sum_count)
        # Рассчитаем положение основных элементов и сохраним данные для отображения
        top             = self._rect.top - self._center + self._scroll.y
        width           = self._rect.width
        self._items     = []
        index           = 0
        for item in data:
            txt         = (str(item.price), str(item.count))
            w           = round(width * (item.count / max_count) * (1 - (self._zoom.x / self._zoom.x_max)))
            x           = self._rect.left
            match item.type:
                case OrderType.ASK:
                    x   = self._rect.right - max(w, 0)
                case OrderType.SEP:
                    w   = width
                    v1  = round((ask_count / sum_count) * 100, 1)
                    v2  = round((bid_count / sum_count) * 100, 1)
                    txt = (f"{v1}%", f"{v2}%", str(data.last_price))
            self._items += [_OrderBookRendererItem(
                text    = txt,
                rect    = self._context.create_rect(self._rect.left, top, width, self._item_height),
                x_rect  = self._context.create_rect(x,               top, w,     self._item_height),
                type    = item.type,
                focused = index == self.focused_item
            )]
            top   += self._item_height + self.P_GAP_HEIGHT
            index += 1

    def render(self):
        ctx = self._context
        ctx.begin()
        # Заливка фоновым цветом
        ctx.set_brush(ctx.create_brush(self.P_BACKGROUND_COLOR))
        ctx.draw_rect(ctx.rect())
        # Нарисуем элементы
        border_pen  = ctx.create_pen(self.P_BORDER_COLOR, self.P_BORDER_WIDTH)
        text_pen    = ctx.create_pen(self.P_TEXT_COLOR, 2)
        empty_brush = ctx.create_brush(None)
        focus_brush = ctx.create_brush(self.P_FOCUS_COLOR)
        sep_brush   = ctx.create_brush(self.P_SEPARATOR_COLOR)
        ask_brush   = ctx.create_brush(self.P_SELL_COLOR)
        bid_brush   = ctx.create_brush(self.P_BUY_COLOR)
        for item in self._items:
            match item.type:
                case OrderType.ASK:
                    brush = ask_brush
                case OrderType.BID:
                    brush = bid_brush
                case OrderType.SEP:
                    brush = sep_brush
                case _:
                    brush = empty_brush
            # Рисуем закрашенную область элемента
            ctx.set_brush(brush)
            ctx.draw_rect(item.x_rect)
            # Рисуем контур элемента
            ctx.set_pen(border_pen)
            ctx.set_brush((item.focused and focus_brush) or empty_brush)
            ctx.draw_rect(item.rect)
            # Выводим текст элемента
            x1 = item.rect.left  + self.P_TEXT_OFFSET
            x2 = item.rect.right - self.P_TEXT_OFFSET - ctx.text_width(item.text[1])
            y  = item.rect.bottom - ((item.rect.height - ctx.text_height()) // 2) - self.P_BORDER_WIDTH*2
            ctx.set_pen((item.type == OrderType.SEP and self.P_SELL_COLOR) or text_pen)
            ctx.draw_text(x1, y, item.text[0])
            ctx.set_pen((item.type == OrderType.SEP and self.P_BUY_COLOR)  or text_pen)
            ctx.draw_text(x2, y, item.text[1])
            if item.type == OrderType.SEP:
                ctx.set_pen(text_pen)
                x3 = item.rect.left + ((item.rect.width - ctx.text_width(item.text[2])) // 2)
                ctx.draw_text(x3, y, item.text[2])
        # Конец
        return ctx.end()