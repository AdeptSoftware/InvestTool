# chart_view.py
from controls.abstract.view         import BaseView
from controls.abstract.source       import AbstractSource


class ChartView(BaseView[AbstractSource]):
    def set_focused_item(self, index):
        self._renderer.set_focused_item(index)
        self._parent.update()