# chart_widget.py
from controls.chart.chart_view              import ChartView, AbstractSource
from controls.chart.chart_renderer          import ChartRenderer
from controls.wrapper.widget                import AdeptWidget
from controls.wrapper.context               import QtContext
from PyQt5.QtWidgets                        import QToolTip, QMenu
from PyQt5.QtCore                           import QPoint

class ChartWidget(AdeptWidget):
    """ Класс виджета графика """
    def __init__(self, parent, source: AbstractSource):
        """
        Конструктор класса виджета графика
        :param parent: родительское окно
        :param source: источник данных
        """
        super().__init__(parent)
        self.view = ChartView(self, source, ChartRenderer(QtContext(self)))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._captured_position is None:
            x = event.pos().x()
            for content, rect in self.view.coordinates():
                if rect.left <= x <= rect.right:
                    QToolTip.showText(event.globalPos() + QPoint(0, 5), content)
                    return
            QToolTip.hideText()

    def contextMenuEvent(self, event):
        menu    = QMenu()
        action1 = menu.addAction("Сбросить")
        action1.triggered.connect(self.view.reset)
        menu.exec(event.globalPos())