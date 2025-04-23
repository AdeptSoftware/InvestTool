# grid.py
from controls.abstract.renderer     import AbstractDynamicRenderer
from controls.abstract.context      import AbstractContext
from controls.abstract.layout       import AbstractLayout
from controls.table.table_model     import TableModel, TableHeaders, TableRow, List

class GridLayout(AbstractLayout):
    """ Слой сетки таблицы """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.GRID_COLOR   = (44, 44, 44)
        self.LINE_OFFSET  = 5

    def render(self, renderer : AbstractDynamicRenderer[TableModel]):
        with renderer.model:
            head    = renderer.model.headers
            rows    = renderer.model.rows
            pen     = self._context.create_pen(*(head.border_color or self.GRID_COLOR), head.border_width)
            offset  = 0 if len(renderer.model.headers.items) != 0 else self.LINE_OFFSET
            # Горизонтальная линия, отделяющая шапку от тела таблицы
            rect    = self._context.rect()
            self._context.set_pen(pen)
            self._context.draw_line(rect.left + offset, head.height, rect.width - (offset * 2), head.height)
            # Горизонтальные линии строк таблицы
            offset  = renderer.scroll.y
            for row in rows:
                if row.rect.bottom + offset < head.height:
                    continue
                if row.rect.bottom + offset > rect.height:
                    continue
                pen = self._context.create_pen(*(row.border_color or self.GRID_COLOR), row.border_width)
                self._context.set_pen(pen)
                self._context.draw_line(rect.left, row.rect.bottom+offset, rect.width, row.rect.bottom+offset)
            # Вертикальные линии
            if len(head.items) > 0:
                offset = renderer.scroll.x
                for header in head.items:
                    if header.rect.right + offset < 0:
                        continue
                    if header.rect.right + offset > rect.width:
                        break
                    pen = self._context.create_pen(*(header.border_color or self.GRID_COLOR), header.border_width)
                    self._context.set_pen(pen)
                    self._context.draw_line(header.rect.right+offset, rect.top, header.rect.right+offset, rect.bottom)
            else:
                dx = rect.width // 3
                dx = [ dx * i for i in range(1, 3) ]
                pen = self._context.create_pen(*self.GRID_COLOR, 1)
                self._context.set_pen(pen)
                for x in dx:
                    self._context.draw_line(x, rect.top + self.LINE_OFFSET, x, rect.bottom - (self.LINE_OFFSET * 2))