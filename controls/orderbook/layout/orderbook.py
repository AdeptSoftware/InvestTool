# orderbook.py
from controls.abstract.context  import AbstractContext, Alignment, Rect, Color
from controls.abstract.element  import AbstractRendererElement, Alignment
from controls.abstract.layout   import AbstractLayout
from dataclasses                import dataclass
from threading                  import RLock
from enum                       import Enum
from typing                     import List
import math


class OrderType(Enum):
    ASK = 0
    BID = 1
    SEP = 2

@dataclass
class OrderBookLayoutItem(AbstractRendererElement):
    x_rect:             Rect                    # прямоугольная область закрашенной части
    focused:            bool                    # элемент в фокусе
    type:               OrderType               # тип элемента
    alignment_volume:   Alignment

    def __init__(self, data, _type):
        self.data               = data
        self.color              = None
        self.background         = None
        self.rect               = None
        self.alignment          = Alignment.LC
        self.padding            = 5

        self.alignment_volume   = Alignment.RC
        self.x_rect             = None
        self.focused            = False
        self.type               = _type



class OrderBookLayout(AbstractLayout):
    """ Слой отрисовки данных стакана """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.ITEM_BORDER_COLOR      = ( 44,  44,  44)
        self.ITEM_FOCUS_COLOR       = (  0,   0,   0)
        self.ITEM_SEPARATOR_COLOR   = (  0,   0,   0)
        self.ITEM_SELL_COLOR        = (255,   0,   0)
        self.ITEM_BUY_COLOR         = (  0, 255,   0)
        self.ITEM_TEXT_COLOR        = (  0, 102, 204)

        self.ITEM_HEIGHT            = 25
        self.ITEM_BORDER_WIDTH      = 1
        self.ITEM_TEXT_SIZE         = 2

        self.scroll_min             = 0
        self.scroll_max             = 0
        self.items                  = []                                                                                # type: List[OrderBookLayoutItem]
        self.lock                   = RLock()

    def render(self, renderer):
        with self.lock:
            ctx = self._context
            border_pen  = ctx.create_pen(*self.ITEM_BORDER_COLOR, self.ITEM_BORDER_WIDTH)
            sep_brush   = ctx.create_brush(*self.ITEM_SEPARATOR_COLOR)
            focus_brush = ctx.create_brush(*self.ITEM_FOCUS_COLOR)
            ask_brush   = ctx.create_brush(*self.ITEM_SELL_COLOR)
            bid_brush   = ctx.create_brush(*self.ITEM_BUY_COLOR)
            empty_brush = ctx.create_brush(None)
            for item in self.items:
                if item.background is None:
                    match item.type:
                        case OrderType.ASK:
                            brush = ask_brush
                        case OrderType.BID:
                            brush = bid_brush
                        case OrderType.SEP:
                            brush = sep_brush
                        case _:
                            brush = empty_brush
                else:
                    brush = ctx.create_brush(*item.background)
                # Рисуем закрашенную область элемента
                ctx.set_brush(brush)
                ctx.draw_rect(item.x_rect)
                # Рисуем контур элемента
                ctx.set_pen(border_pen)
                ctx.set_brush(focus_brush if item.focused else empty_brush)
                ctx.draw_rect(item.rect)
                # Выводим цену
                sym = '%' if item.type == OrderType.SEP else ''
                self.set_pen(item.color, item.type == OrderType.SEP, self.ITEM_SELL_COLOR, self.ITEM_TEXT_COLOR)
                ctx.draw_text_ex(item.rect, str(item.data[0]) + sym, item.alignment)
                # Выводим объем торгов
                self.set_pen(item.color, item.type == OrderType.SEP, self.ITEM_BUY_COLOR, self.ITEM_TEXT_COLOR)
                ctx.draw_text_ex(item.rect, str(item.data[1]) + sym, item.alignment_volume)
                # Выводи текущую цену
                if item.type == OrderType.SEP:
                    ctx.set_pen(ctx.create_pen(*self.ITEM_TEXT_COLOR, self.ITEM_TEXT_SIZE))
                    ctx.draw_text_ex(item.rect, str(item.data[2]), Alignment.CC)

    def set_pen(self, custom_color, condition, color_true, color_false):
        if custom_color:
            pen = self._context.create_pen(*custom_color, self.ITEM_TEXT_SIZE)
        elif condition:
            pen = self._context.create_pen(*color_true,   self.ITEM_TEXT_SIZE)
        else:
            pen = self._context.create_pen(*color_false,  self.ITEM_TEXT_SIZE)
        self._context.set_pen(pen)

    def update(self, orderbook, last_price, scroll, zoom, focused_item):
        assert (orderbook is not None)
        if len(orderbook) == 0:
            return
        with self.lock:
            self.items = []
            sep = self.create_separator_item(orderbook, last_price)
            self.items.extend(self.convert(orderbook, OrderType.ASK))
            self.items.append(sep)
            self.items.extend(self.convert(orderbook, OrderType.BID))
            self.recalculate_rect(scroll, zoom, sep.data[3], focused_item)

    def calculate_bounds(self, zoom_y):
        client_height    = self._context.rect().height
        item_height      = self.ITEM_HEIGHT + zoom_y
        visible_count    = math.floor(client_height / item_height)
        max_scroll       = (max(0, len(self.items) - visible_count) * item_height)

        index            = 0
        for index, item in enumerate(self.items):
            if item.type == OrderType.SEP:
                break

        center           = math.floor(item_height * (index - 0.5))
        center          -= math.floor(client_height / 2)
        self.scroll_min  = center - max_scroll
        self.scroll_max  = center
        return item_height, center

    @staticmethod
    def create_separator_item(orderbook, last_price) -> OrderBookLayoutItem:
        max_count = 1
        count     = [ 0, 0 ]
        for index, items in enumerate(orderbook):
            for item in items:
                max_count = max(item.count, max_count)
                count[index] += item.count
        sum_count = max(1, sum(count))

        v1 = round((count[0] / sum_count) * 100, 1)
        v2 = round((count[1] / sum_count) * 100, 1)
        return OrderBookLayoutItem(data=(v1, v2, last_price, max_count), _type=OrderType.SEP)

    @staticmethod
    def convert(orderbook, _type: OrderType):
        items = []
        for item in orderbook[_type.value]:
            items.append(OrderBookLayoutItem(data=(item.price, item.count), _type=_type))
        return items

    def recalculate_rect(self, scroll, zoom, _max, focused_index):
        height, center   = self.calculate_bounds(zoom.y)
        rect             = self._context.rect()
        top              = rect.top - center + scroll.y
        width            = rect.width
        factor           = 0 if zoom.x_max == 0 else zoom.x / zoom.x_max
        for index, item in enumerate(self.items):
            w            = round(width * (item.data[1] / _max) * (1 - factor))
            x            = rect.left
            match item.type:
                case OrderType.ASK:
                    x    = rect.right - max(w, 0)
                case OrderType.SEP:
                    w    = width
            item.rect    = self._context.create_rect(rect.left, top, width, height)
            item.x_rect  = self._context.create_rect(x,         top, w,     height)
            item.focused = index == focused_index
            top         += height