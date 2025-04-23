# chart_widget.py
from controls.chart.chart_renderer  import ChartRenderer
from controls.chart.chart_view      import ChartView
from controls.wrapper.widget        import Widget
from controls.wrapper.context       import QtContext
from PyQt5.QtWidgets                import QWidget, QToolTip, QMenu, QAction
from PyQt5.QtCore                   import QPoint

from controls.chart.layout.change   import ChangeLayout

class ChartWidget(Widget):
    """ Класс виджета графика """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._renderer = ChartRenderer(QtContext(self))
        self.view      = ChartView(self, self._renderer)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._captured_position is None:
            index, item = self.view.get_element(event.pos().x(), event.pos().y())
            if item:
                self.view.set_focused_item(index)
                self.view.update()
                QToolTip.showText(event.globalPos() + QPoint(0, 5), str(item.data))
            QToolTip.hideText()

    def contextMenuEvent(self, event):
        menu = QMenu()
        self._ctx_action(menu, "Сбросить", self._reset)
        self._ctx_action(menu, "Изменение за день", self._switch_chg_mode, self._renderer[ChangeLayout].show_by_day)
        self._ctx_action(menu, "Показывать изменение цены", self._switch_shw_mode, self._renderer[ChangeLayout].show_price)
        menu.exec(event.globalPos())

    @staticmethod
    def _ctx_action(menu, text, fn, checked=False):
        action = menu.addAction(text)
        action.triggered.connect(fn)
        action.setCheckable(checked)
        action.setChecked(checked)

    def _reset(self):
        self.view.reset()
        self.view.update()

    def _switch_chg_mode(self):
        layout = self._renderer[ChangeLayout]
        layout.show_by_day = not layout.show_by_day
        self.view.update()

    def _switch_shw_mode(self):
        layout = self._renderer[ChangeLayout]
        layout.show_price = not layout.show_price
        self.view.update()