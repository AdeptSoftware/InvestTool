# body.py
from controls.abstract.renderer     import AbstractDynamicRenderer
from controls.abstract.renderer     import AbstractLayout
from controls.abstract.context      import AbstractContext
from controls.table.table_model     import TableModel, TableRow, List

class BodyLayout(AbstractLayout):
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.ITEM_BORDER_COLOR      = ( 44,  44,  44)
        self.ITEM_BACKGROUND_COLOR  = ( 28,  28,  28)
        self.ITEM_FOCUS_COLOR       = (  0,   0,   0)
        self.ITEM_TEXT_COLOR        = (255, 255, 255)

    def render(self, renderer: AbstractDynamicRenderer[TableModel]):
        with renderer.model:
            dx = renderer.scroll.x
            dy = renderer.scroll.y
            rect = self._context.rect()
            for row_index, row in enumerate(renderer.model.rows):
                rc = row.rect.adjusted(0, dy, 0, dy)
                if not rc.intersect(rect):
                    continue
                
                for item in row.items:
                    rc = item.rect.adjusted(dx+1, dy, dx+1, dy)
                    if not rc.intersect(rect):
                        continue

                    if row_index == renderer.get_focused_index():
                        bkg_brush = self._context.create_brush(*self.ITEM_FOCUS_COLOR)
                    else:
                        bkg_brush = self._context.create_brush(*(item.background or self.ITEM_BACKGROUND_COLOR))
                    self._context.set_pen(None)
                    self._context.set_brush(bkg_brush)
                    self._context.draw_rect(rc)

                    pen = self._context.create_pen(*(item.color or self.ITEM_TEXT_COLOR), 1)
                    self._context.set_pen(pen)
                    self._context.draw_text_ex(rc, str(item.data), item.alignment, item.padding)