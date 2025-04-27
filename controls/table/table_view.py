# table_view.py
from controls.abstract.view         import BaseView
from controls.table.table_model     import TableModel

class TableView(BaseView[TableModel]):
    def set_focused_item(self, col=None, row=None):
        self._renderer.set_focused_item(-1 if col is None else col,
                                        -1 if row is None else row)
        self._parent.update()

