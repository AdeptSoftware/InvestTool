# change.py
from controls.abstract.context  import AbstractContext
from controls.abstract.layout   import AbstractLayout
from controls.utils.functions   import round_x
from datetime                   import datetime, timedelta
import math

class ChangeLayout(AbstractLayout):
    """ Слой фона """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.TEXT_PEN       = ctx.create_pen(255, 102, 0)
        self.TEXT_OFFSET    = ctx.create_point(5, 5)
        self.TEXT_FONT      = ctx.create_font("Arial", 10, bold=True)

        self._text          = ""
        self.show_by_day    = True
        self.show_price     = False

    def update(self, items, first, last):
        if len(items) > 0:
            _date = ""
            if self.show_by_day:
                t = items[last].date
                if t.date() != datetime.now().date():
                    _date = items[last].date.strftime("%D  ")
                _open, _close = self._open_day_price(items, t)
            else:
                _open, _close = items[first].open, items[last].close
            self._text = f"{_date}{self._2str(_open, _close)}"
            if self.show_price:
                self._text += f" {_open}→{_close}"
        else:
            self._text = ""

    @staticmethod
    def _2str(_open, _close):
        _diff = round_x(_close - _open)
        if _diff != 0:
            _perc = round_x(round(math.fabs((_close / _open) - 1) * 100, 2))
            _prex  = (_diff > 0 and "+") or ""
            return f"{_prex}{_diff} ₽  {_perc}%"
        return ""

    @staticmethod
    def _open_day_price(items, _time: datetime):
        start  = _time.replace(hour=0, minute=0, second=0, microsecond=0)
        end    = start + timedelta(days=1)
        _items = items[start:end]
        if _items:
            return _items[0].open, _items[-1].close
        return 0, 0

    def render(self):
        font = self._context.set_font(self.TEXT_FONT)
        self._context.set_pen(self.TEXT_PEN)
        self._context.draw_text(self.TEXT_OFFSET.x, self.TEXT_OFFSET.y + self._context.text_height(), self._text)
        self._context.set_font(font)