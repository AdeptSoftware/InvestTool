# table_renderer.py
from controls.abstract.renderer         import AbstractDynamicRenderer, AbstractRendererElement
from controls.abstract.context          import AbstractContext, Rect
from controls.table.table_model         import TableModel, TableItem, EventMethod

from controls.layout.background         import BackgroundLayout
from controls.table.layout.header       import HeaderLayout
from controls.table.layout.grid         import GridLayout
from controls.table.layout.body         import BodyLayout


class TableRenderer(AbstractDynamicRenderer[TableModel]):
    def __init__(self, ctx: AbstractContext):
        ctx.set_font(ctx.create_font("Arial", 10))
        super().__init__(ctx, TableModel([]))

        self._layouts       += [
            BackgroundLayout(ctx),
            BodyLayout(ctx),
            HeaderLayout(ctx),
            GridLayout(ctx)
        ]

        self._focused_index  = -1
        self._focused_column = -1

    def get_focused_index(self):
        return self._focused_index

    def get_focused_column(self):
        return self._focused_column

    def set_focused_item(self, col, row):
        self._focused_index  = max(-1, min(row, len(self._model.rows)))
        self._focused_column = max(-1, min(col, len(self._model.headers.items)))

    def get_element(self, x, y) -> (int, AbstractRendererElement):
        with self._model:
            x -= self._scroll.x
            for index, header in enumerate(self._model.headers.items):
                if header.rect and header.rect.contain(x, y):
                    return index, header
            y -= self._scroll.y
            for index, row in enumerate(self._model.rows):
                for item in row.items:
                    if item.rect and item.rect.contain(x, y):
                        return index, item
        return None, None


    def prepare(self):
        with self._model:
            self._model.update(self._context)                                                                           # noqa

            right  = 0 if len(self._model.headers.items) == 0 else self._model.headers.items[-1].rect.right
            bottom = self._model.headers.height
            if len(self._model.rows) != 0:
                count = len(self._model.rows) - 1
                for row in self._model.rows:
                    if row.order == count:
                        bottom = row.rect.bottom
                        break

            rect = self._context.rect()
            self._scroll.x_min = 0 if rect.width  - right  > 0 else rect.width  - right
            self._scroll.y_min = 0 if rect.height - bottom > 0 else rect.height - bottom



