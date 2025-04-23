# chart_view.py
from controls.abstract.widget       import AbstractWidget
from controls.abstract.view         import AbstractView
from controls.abstract.source       import AbstractSource
from controls.chart.chart_renderer  import ChartRenderer


class ChartView(AbstractView[AbstractSource]):
    def __init__(self, parent: AbstractWidget, renderer: ChartRenderer):
        super().__init__(parent, renderer)

    def update(self):
        self._renderer.update()
        self._parent.update()

    def set_focused_item(self, index):
        self._renderer.set_focused_item(index)