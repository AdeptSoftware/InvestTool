# table_view.py
from controls.abstract.widget       import AbstractWidget
from controls.abstract.view         import AbstractView
from controls.table.table_renderer  import TableRenderer
from controls.table.table_model     import TableModel, TableHeaders

class TableView(AbstractView[TableModel]):
    def __init__(self, parent: AbstractWidget, renderer: TableRenderer):
        super().__init__(parent, renderer)

    def update(self):
        self._renderer.update()

    def set_update_callback(self, callback):
        self._renderer.update.connect(callback)

    def set_focused_item(self, col=None, row=None):
        self._renderer.set_focused_item(-1 if col is None else col,
                                        -1 if row is None else row)

