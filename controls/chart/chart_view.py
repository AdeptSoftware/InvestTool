# chart_view.py
from controls.abstract.renderer import AbstractDynamicRenderer
from controls.abstract.widget   import AbstractWidget
from controls.abstract.view     import AbstractView


class ChartView(AbstractView):
    """ Класс графика """
    def __init__(self, parent : AbstractWidget, renderer: AbstractDynamicRenderer):
        super().__init__(parent, renderer)
        renderer.P_DEFAULT_ZOOM_Y = 3