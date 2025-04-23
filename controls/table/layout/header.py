# header.py
from controls.abstract.renderer     import AbstractDynamicRenderer
from controls.abstract.renderer     import AbstractLayout
from controls.abstract.context      import AbstractContext
from controls.table.table_model     import TableModel, TableHeaders

class HeaderLayout(AbstractLayout):
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.HEADER_BORDER_COLOR        = ( 44,  44,  44)
        self.HEADER_BACKGROUND_COLOR    = ( 28,  28,  28)
        self.HEADER_FOCUS_COLOR         = (  0,   0,   0)
        self.HEADER_TEXT_COLOR          = (255, 255, 255)
        self.TRIANGLE_COLOR             = (255, 255, 255)
        self.TRIANGLE_WIDTH             = 10
        self.TRIANGLE_HEIGHT            = 6
        self.TRIANGLE_OFFSET            = 5

    def render(self, renderer : AbstractDynamicRenderer[TableModel]):
        with renderer.model:
            dx = renderer.scroll.x
            rect = self._context.rect()
            head = renderer.model.headers
            sort_index, descending = renderer.model.current_sorted_parameters()
            for index, header in enumerate(head.items):
                rc = header.rect.adjusted(dx, 0, dx, 0)
                if not rc.intersect(rect):
                    continue
                # Заливка
                if index == renderer.get_focused_column():
                    bkg_brush = self._context.create_brush(*self.HEADER_FOCUS_COLOR)
                else:
                    bkg_brush = self._context.create_brush(*(header.background or self.HEADER_BACKGROUND_COLOR))
                self._context.set_pen(None)
                self._context.set_brush(bkg_brush)
                self._context.draw_rect(rc)
                # Текст
                pen = self._context.create_pen(*(header.color or self.HEADER_TEXT_COLOR), 1)
                self._context.set_pen(pen)
                self._context.draw_text_ex(rc, str(header.data), header.alignment, header.padding)
                # Отображаем тип сортировки
                if index == sort_index:
                    self._context.set_pen(None)
                    self._context.set_brush(self._context.create_brush(*self.TRIANGLE_COLOR))
                    self._context.draw_polygon(self.create_triangle(rc.right, rc.height, descending))

    def create_triangle(self, right, height, inverse):
        right -= self.TRIANGLE_OFFSET
        dy     = self.TRIANGLE_HEIGHT
        h      = (height - dy) // 2
        if not inverse:
            h += dy
            dy = -dy
        return [
            self._context.create_point(right, h),
            self._context.create_point(right - self.TRIANGLE_WIDTH, h),
            self._context.create_point(right - (self.TRIANGLE_WIDTH // 2), h + dy)
        ]