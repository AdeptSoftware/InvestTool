# table_widget_ex.py
""" Обычный QTableWidget по какой-то причине не может очень быстро обновлять много данных """
from controls.wrapper.widget        import Widget
from controls.table.table_view      import TableView
from controls.table.table_model     import TableModel, TableHeader, TableItem, AbstractRendererElement
from controls.table.table_renderer  import TableRenderer
from controls.wrapper.context       import QtContext

from PyQt5.QtGui                    import QMouseEvent
from PyQt5.QtWidgets                import QWidget, QGridLayout, QScrollBar
from PyQt5.QtCore                   import Qt

class _TableWidgetEx(Widget):
    DRAG_RANGE = 10

    def __init__(self, parent):
        super().__init__(parent)
        self._context        = QtContext(self)
        self.view            = TableView(self, TableRenderer(self._context))
        self._captured_item  = None                                                                                     # type: AbstractRendererElement
        self._captured_index = None                                                                                     # type: int
        self._captured_grid  = False

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._captured_index, self._captured_item = self.view.get_element(event.pos().x(), event.pos().y())
            if self._captured_item:
                if isinstance(self._captured_item, TableItem):
                    with self.view.model:
                        self._captured_item = self.view.model.rows[self._captured_index]
                    y = event.pos().y() - self.view.scroll.y
                    if self._captured_item.resizable and y + self.DRAG_RANGE > self._captured_item.rect.bottom:
                        self._captured_grid = True
                else:
                    x = event.pos().x() - self.view.scroll.x
                    if self._captured_item.resizable and x + self.DRAG_RANGE > self._captured_item.rect.right:
                        self._captured_grid = True

    def mouseMoveEvent(self, event):
        if self._captured_position is None:
            index, item = self.view.get_element(event.pos().x(), event.pos().y())
            if not item:
                self.view.set_focused_item(None)
            else:
                if isinstance(item, TableHeader):
                    self.view.set_focused_item(col=index)
                else:
                    self.view.set_focused_item(row=index)
            self.view.update()
        if self._captured_grid:
            offset = event.pos() - self._captured_position
            if isinstance(self._captured_item, TableHeader):
                x = event.pos().x() - self.view.scroll.x
                if x >= self._captured_item.rect.left + self.DRAG_RANGE:                                  # Запрещаем уводить правую границу левее левой
                    self._captured_item.width = max(self.DRAG_RANGE, self._captured_item.rect.width + offset.x())
                    self._captured_position = event.pos()
                    self.view.update()
            else:
                y = event.pos().y() - self.view.scroll.y
                if y >= self._captured_item.rect.top + self.DRAG_RANGE:
                    self._captured_item.height = max(self.DRAG_RANGE, self._captured_item.rect.height + offset.y())
                    self._captured_position = event.pos()
                    self.view.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            # Сортировка элементов таблицы
            if isinstance(self._captured_item, TableHeader):
                column, descending = self.view.model.current_sorted_parameters()
                self.view.model.sort(self._captured_index, not descending if self._captured_index == column else True)
                self.view.update()
            # Очищаем
            self._captured_item  = None
            self._captured_index = None
            self._captured_grid  = False

    def leaveEvent(self, event):
        self.view.set_focused_item(None)
        super().leaveEvent(event)


class TableWidgetEx(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.table      = _TableWidgetEx(self)
        self.v_scroll   = QScrollBar(Qt.Vertical, self)
        self.h_scroll   = QScrollBar(Qt.Horizontal, self)

        layout = QGridLayout(self)
        layout.addWidget(self.table,    0, 0)
        layout.addWidget(self.v_scroll, 0, 1)
        layout.addWidget(self.h_scroll, 1, 0)

        layout.setColumnStretch(0, 1)
        layout.setRowStretch(0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.v_scroll.valueChanged.connect(self._on_scroll)
        self.h_scroll.valueChanged.connect(self._on_scroll)

        self.table.view.set_update_callback(self._on_update)

    def _on_scroll(self):
        self.table.view.scroll.x = -self.h_scroll.value()
        self.table.view.scroll.y = -self.v_scroll.value()
        self.table.view.update()

    def _on_update(self):
        self.h_scroll.setValue(-self.view.scroll.x)
        self.v_scroll.setValue(-self.view.scroll.y)
        self.h_scroll.setMaximum(-self.view.scroll.x_min)
        self.v_scroll.setMaximum(-self.view.scroll.y_min)

    @property
    def view(self):
        return self.table.view