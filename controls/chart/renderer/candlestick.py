# line.py
from controls.abstract.renderer import AbstractDynamicRenderer, Limits
from controls.abstract.context  import AbstractContext, Rect
import datetime
import math
import sys

def interpolate(y0, y1, x0, x1, x):
    """ Интерполяция данных """
    return y0 + ((y1 - y0) * ((x - x0) / (x1 - x0)))

def frange(start, end, step):
    pos  = start
    base = math.ceil(math.fabs(math.log10(math.fabs(step))))
    while (step > 0 and pos <= end) or (step < 0 and pos >= end):
        yield round(pos, base)
        pos += step

class CandlestickRenderer(AbstractDynamicRenderer):
    """ Класс свечного графика """
    def __init__(self, ctx : AbstractContext):
        """
        Конструктор класса
        :param ctx: контекст рисования
        """
        super().__init__(ctx)
        ctx.set_font("Arial", 10)

        self.P_CANDLE_BORDER_WIDTH  = 1
        self.P_GAP_WIDTH            = 3
        self.P_WICK_WIDTH           = 1
        self.P_GRID_LINE_WIDTH      = 5
        self.P_TICK_INTERVAL        = 5
        self.P_CANDLE_WIDTH         = 12
        self.P_BORDER_WIDTH         = 5
        self.P_EQUAL_MODIFIER       = 0.05
        self.P_DOWN_COLOR           = ctx.create_color(210,  52,  43)
        self.P_DOWN_BORDER_COLOR    = ctx.create_color(216,  73,  67)
        self.P_UP_COLOR             = ctx.create_color(  6, 170,  84)
        self.P_UP_BORDER_COLOR      = ctx.create_color( 38, 185, 107)
        self.P_GRID_COLOR           = ctx.create_color( 44,  44,  44)
        self.P_BACKGROUND_COLOR     = ctx.create_color( 28,  28,  28)
        self.P_TICK_COLOR           = ctx.create_color(128, 128, 128)

        self._right_offset          = None
        self._candle_width          = None
        self._element_width         = None
        self._candles               = None
        self._x_min                 = None
        self._x_max                 = None
        self._y_min                 = None
        self._y_max                 = None
        self._h_cnt                 = None
        self._rect                  = None
        self.update()

    def coordinates(self) -> (str, Rect):
        """ Генератор, возвращающий координаты элементов графика """
        for candle in self._candles or []:
            yield str(candle), candle.rect["body"]

    def update(self):
        """ Обновление данных отрисовщика """
        self._rect = self._context.rect().adjusted(
            self.P_BORDER_WIDTH,
            self.P_BORDER_WIDTH,
            - (self.P_BORDER_WIDTH + self.P_GAP_WIDTH) * 2,
            - (self.P_BORDER_WIDTH * 2 + self.P_GAP_WIDTH + self._context.text_height())
        )
        x_min = 1 - self.P_CANDLE_WIDTH
        x_max = self._rect.width // self.P_TICK_INTERVAL
        self._candle_width   = self.P_CANDLE_WIDTH + self._zoom.x
        self._right_offset   = self._candle_width // 2
        self._element_width  = self.P_CANDLE_WIDTH + self._zoom.x + self.P_GAP_WIDTH
        self._zoom_limits   = Limits(x_min=x_min, x_max=x_max,       y_min=0, y_max=50)
        self._scroll_limits = Limits(x_min=0,     x_max=sys.maxsize, y_min=0, y_max=0)

    def set(self, data):
        """ Обработка входных данных перед рендером """
        assert (data is not None)
        assert (len(data) != 0)
        self.update()
        # Определим предварительные границы данных
        cnt = len(data)
        first = max(1, 1 + math.floor(self._scroll.x / self._element_width))
        last  = min(cnt, first + math.ceil(self._rect.width / self._element_width))  # Предварительно
        # Найдем максимальную длину текста цены
        s_max = 0
        for candle in data[-first:-last:-1]:
            s_max = max(
                self._context.text_width(str(candle.close)),
                self._context.text_width(str(candle.high)),
                self._context.text_width(str(candle.low)),
                self._context.text_width(str(candle.open))
            )
        # Обновим данные об области графика
        self._rect.width = self._rect.width - s_max - self.P_BORDER_WIDTH
        last = min(cnt, first + math.ceil(self._rect.width / self._element_width))
        self._candles = data[-first:-last:-1]
        if len(self._candles) != 0:
            # Найдем максимальные и минимальные значения
            self._x_min = self._x_max = self._y_min = self._y_max = None
            for candle in self._candles:
                self._y_min = min(self._y_min or candle.low, candle.low)
                self._y_max = max(self._y_max or candle.high, candle.high)
                self._x_min = min(self._x_min or candle.index, candle.index)
                self._x_max = max(self._x_max or candle.index, candle.index)
            # Модифицируем данные, если они не имеют разбега по значениям
            if self._y_max == self._y_min:
                self._y_min *= 1 - self.P_EQUAL_MODIFIER
                self._y_max *= 1 + self.P_EQUAL_MODIFIER

            if self._x_max == self._x_min:
                self._x_min -= datetime.timedelta(minutes=1)
                self._x_max += datetime.timedelta(minutes=1)
            # Добавим масштаб по оси Y
            offset = self._zoom.y * ((self._y_max - self._y_min) / 20)
            self._y_min -= offset
            self._y_max += offset
            # Вычислим прямоугольные области свечей
            self._y_min, self._y_max, self._h_cnt = self._h_lines_count()
            self._rects()                                                                                               # название такое себе

    def render(self):
        """ Рендер данных """
        ctx = self._context
        ctx.begin()
        # Заливка фоновым цветом
        ctx.set_brush(ctx.create_brush(self.P_BACKGROUND_COLOR))
        ctx.draw_rect(ctx.rect())
        if len(self._candles) != 0:
            # Рисуем вертикальные и горизонтальные линии сетки
            v_lines = self._vertical_lines()
            h_lines = self._horizontal_lines()
            ctx.set_pen(ctx.create_pen(self.P_GRID_COLOR, self.P_GRID_LINE_WIDTH))
            for line in v_lines:
                ctx.draw_line(line["pos"], self._rect.top, line["pos"], self._rect.bottom)
            for line in h_lines:
                ctx.draw_line(self._rect.left, line["pos"], self._rect.right, line["pos"])
            # Рисуем отметки к вертикальным и горизонтальным линиям сетки
            x = self._rect.right + self.P_GRID_LINE_WIDTH + self.P_GAP_WIDTH
            y = self._rect.bottom + self._context.text_height() + self.P_GAP_WIDTH
            ctx.set_pen(ctx.create_pen(self.P_TICK_COLOR, 1))
            for line in v_lines:
                ctx.draw_text(line["coord"], y, line["tick"])
            for line in h_lines:
                ctx.draw_text(x, line["coord"], line["tick"])
            # Отрисовываваем свечи
            r_brush = ctx.create_brush(self.P_DOWN_COLOR)
            g_brush = ctx.create_brush(self.P_UP_COLOR)
            r_pen   = ctx.create_pen(self.P_DOWN_BORDER_COLOR, self.P_CANDLE_BORDER_WIDTH)
            g_pen   = ctx.create_pen(self.P_UP_BORDER_COLOR,   self.P_CANDLE_BORDER_WIDTH)
            for candle in self._candles:
                if candle.close > candle.open:
                    ctx.set_brush(g_brush)
                    ctx.set_pen(g_pen)
                else:
                    ctx.set_brush(r_brush)
                    ctx.set_pen(r_pen)
                ctx.draw_rect(candle.rect["wick"])
                ctx.draw_rect(candle.rect["body"])
        # Конец
        return ctx.end()

    def _vertical_lines(self):
        """ Определим координаты и подписи к вертикальным линиям """
        lines = []
        x = self._rect.right - self._right_offset
        for candle in self._candles[::self.P_TICK_INTERVAL]:
            text = candle.index.strftime("%H:%M")
            size = self._context.text_width(text)
            lines += [{
                "pos": x,  # позиция сетки
                "coord": x - (size // 2),  # верхний правый угол надписи
                "tick": text,
                "size": size,
                "show": True
            }]
            x -= (self.P_TICK_INTERVAL * self._element_width)
        return self._check_lines(lines, 1)

    def _horizontal_lines(self):
        """ Определим координаты и подписи к горизонтальным линиям """
        lines = []
        y = self._rect.bottom
        _step = (self._y_max - self._y_min) / self._h_cnt
        offset = round(self._rect.height / self._h_cnt)
        for value in frange(self._y_min, self._y_max+_step, _step):
            lines += [{
                "pos":      y,
                "coord":    y + (self._context.text_height() // 2) - self.P_GRID_LINE_WIDTH,
                "tick":     str(value),
                "size":     self._context.text_height(),
                "show":     True
            }]
            y -= offset
        return self._check_lines(lines, self._context.text_height() - self.P_BORDER_WIDTH)

    def _rects(self):
        """ Вычисление прямоугольных областей свечей """
        x = self._rect.right - self._right_offset
        coord = (self._rect.bottom, self._rect.top)
        for candle in self._candles:
            y_min = round(interpolate(coord[0], coord[1], self._y_min, self._y_max, min(candle.open, candle.close)))
            y_max = round(interpolate(coord[0], coord[1], self._y_min, self._y_max, max(candle.close, candle.open)))
            y0    = round(interpolate(coord[0], coord[1], self._y_min, self._y_max, candle.low))
            y1    = round(interpolate(coord[0], coord[1], self._y_min, self._y_max, candle.high))

            rect = {
                "body": self._context.create_rect(
                    x - (self._candle_width // 2),
                    y_min,
                    self._candle_width,
                    y_max - y_min
                ),
                "wick": self._context.create_rect(
                    x - (self.P_WICK_WIDTH // 2),
                    y0,
                    self.P_WICK_WIDTH,
                    y1 - y0
                )
            }
            candle.rect = rect
            x -= self._element_width

    def _check_lines(self, lines, _min):
        """ Проверка линий на выход запределы графика по оси X """
        if len(lines) > 1:
            last = lines[0]["coord"]
            for line in lines[1:]:
                if last < line["coord"] + line["size"] + self.P_GAP_WIDTH:
                    line["show"] = False
                else:
                    if line["coord"] < _min:
                        if last >= _min + line["size"] + self.P_GAP_WIDTH:
                            line["coord"] = _min
                        else:
                            line["show"] = False
                            continue
                    last = line["coord"]
        return [line for line in lines if line["show"]]

    def _h_lines_count(self):
        """ Определяет количество линий по оси Y и их диапазон"""
        _diff = self._y_max - self._y_min
        _base = math.pow(10, math.floor(math.log10(_diff)))
        _min  = _base *  (self._y_min // _base)
        _max  = _base * ((self._y_max // _base) + 1)

        if (_max - self._y_max) / _base > 0.5:
            _max -= _base * 0.5
        if (self._y_min - _min) / _base > 0.5:
            _min += _base * 0.5

        _cnt  = 0
        delta = math.ceil((_max - _min) / (_base / 10))
        for _cnt in range(self._rect.height // (self._context.text_height() + self.P_GAP_WIDTH), 1, -1):
            if delta % _cnt == 0:
                break

        return _min, _max, _cnt
