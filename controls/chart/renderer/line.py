# line.py
from controls.chart.renderer.candlestick import CandlestickRenderer, AbstractContext

class LineRenderer(CandlestickRenderer):
    def __init__(self, context : AbstractContext):
        super().__init__(context)

    def render(self):
        pass
