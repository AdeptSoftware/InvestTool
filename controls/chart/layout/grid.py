# grid.py
from controls.abstract.context import AbstractContext
from controls.abstract.layout  import AbstractLayout
from controls.utils.functions  import frange

class GridLayout(AbstractLayout):
    """ Слой сетки """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.LINE_WIDTH         = 5
        self.TICK_INTERVAL      = 5
        self.TICK_GAP           = 3

        self.LINE_PEN           = ctx.create_pen( 44,  44,  44, self.LINE_WIDTH)
        self.TICK_PEN           = ctx.create_pen(128, 128, 128)

        self._vertical_lines    = []
        self._horizontal_lines  = []
        self.index2str          = lambda x: str(x)

    def set_vertical_lines(self, items, width, rect):
        """
        Определим координаты и подписи к вертикальным линиям
        :param items: данные типа AbstractData
        :param width: ширина одного item+отступ
        :param rect:  область отрисовки сетки
        """
        lines    = []
        x        = rect.right - (width // 2)
        u        = rect.bottom + self._context.text_height() + self.TICK_GAP
        for item in items[::self.TICK_INTERVAL]:
            text = self.index2str(item.index)
            size = self._context.text_width(text)
            lines += [{
                "x":        x,                                          # x1 и x2 вертикальной линии сетки
                "y1":       rect.top,                                   # y1 вертикальной линии сетки
                "y2":       rect.bottom,                                # y2 вертикальной линии сетки
                "w":        x - (size // 2),                            # верхний правый угол надписи (x)
                "u":        u,                                          # верхний правый угол надписи (y)
                "size":     size,                                       # ширина текста
                "tick":     text,                                       # текст отметки
                "show":     True                                        # служебное
            }]
            x -= (self.TICK_INTERVAL * width)
        self._vertical_lines = self._check_lines(lines, rect.left)

    def set_horizontal_lines(self, y_min, y_max, count, rect):
        """
        Определим координаты и подписи к горизонтальным линиям
        :param y_min: минимальное значение по оси Y
        :param y_max: максимальное значение по оси Y
        :param count: количество линий
        :param rect:  область отрисовки сетки
        """
        lines  = []
        y      = rect.bottom
        _step  = (y_max - y_min) / count
        offset = round(rect.height / count)
        height = self._context.text_height()
        u      = rect.right + self.TICK_GAP + self.LINE_WIDTH
        for value in frange(y_min, y_max + _step, _step):
            lines += [{
                "y":        y,                                          # y1, y2 горизонтальной линии сетки
                "x1":       rect.left,                                  # x1 горизонтальной линии сетки
                "x2":       rect.right,                                 # x2 горизонтальной линии сетки
                "w":        y + (height // 2) - self.LINE_WIDTH,        # верхний правый угол надписи (y)
                "u":        u,                                          # верхний правый угол надписи (x)
                "size":     height,                                     # высота текста
                "tick":     str(value),                                 # текст отметки
                "show":     True                                        # служебное
            }]
            y -= offset
        self._horizontal_lines = self._check_lines(lines, rect.top + height)

    def _check_lines(self, lines, _min):
        """
        Проверка линий на выход запределы графика
        :param lines: список линий
        :param _min:  минимально допустимое значение
        :return:
        """
        if len(lines) > 1:
            last = lines[0]["w"]
            for line in lines[1:]:
                if last < line["w"] + line["size"] + self.TICK_GAP:
                    line["show"] = False
                else:
                    if line["w"] < _min:
                        if last >= _min + line["size"] + self.TICK_GAP:
                            line["w"] = _min
                        else:
                            line["show"] = False
                            continue
                    last = line["w"]
        return [line for line in lines if line["show"]]


    def render(self, renderer):
        self._context.set_pen(self.LINE_PEN)
        for line in self._vertical_lines:
            self._context.draw_line(line["x"], line["y1"], line["x"], line["y2"])
        for line in self._horizontal_lines:
            self._context.draw_line(line["x1"], line["y"], line["x2"], line["y"])

        self._context.set_pen(self.TICK_PEN)
        for line in self._vertical_lines:
            self._context.draw_text(line["w"], line["u"], line["tick"])
        for line in self._horizontal_lines:
            self._context.draw_text(line["u"], line["w"], line["tick"])