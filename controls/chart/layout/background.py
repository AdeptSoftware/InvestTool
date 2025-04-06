# background.py
from controls.abstract.context import AbstractContext
from controls.abstract.layout  import AbstractLayout

class BackgroundLayout(AbstractLayout):
    """ Слой фона """
    def __init__(self, ctx: AbstractContext, visible=True):
        super().__init__(ctx, visible)
        self.BACKGROUND_BRUSH = ctx.create_brush(28, 28, 28)

    def render(self):
        self._context.set_brush(self.BACKGROUND_BRUSH)
        self._context.draw_rect(self._context.rect())