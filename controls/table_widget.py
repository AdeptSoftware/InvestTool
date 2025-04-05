from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore    import QAbstractTableModel, Qt
from enum            import Enum, IntEnum

class ColumnType(IntEnum):
    NAME     = 0,
    CONTENT  = 1

class _TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(_TableModel, self).__init__()
        self._headers = ("Название", "Значение")
        self._data = data

    def data(self, index, role = ...):
        if role == Qt.DisplayRole:
            key = list(self._data.keys())[index.row()]
            if index.column() == 0:
                return key
            return self._data[key]

    def rowCount(self, parent = ...):
        return len(self._data)

    def columnCount(self, parent = ...):
        if self._data:
            return len(self._headers)
        return 0

    def headerData(self, section, orientation, role = ...):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return f"{section}"

class TableWidget(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self._data  = {}
        self.setStyleSheet("""
            QHeaderView::section
            {
                border-top:         0px solid #D8D8D8;
                border-left:        0px solid #D8D8D8;
                border-right:       1px solid #D8D8D8;
                border-bottom:      1px solid #D8D8D8;
                background-color:   white;
                padding:            4px;
            }
            QTableCornerButton::section
            {
                border-top:         0px solid #D8D8D8;
                border-left:        0px solid #D8D8D8;
                border-right:       1px solid #D8D8D8;
                border-bottom:      1px solid #D8D8D8;
                background-color:   white;
            }
            """)

        model = _TableModel(self._data)

        header = self.verticalHeader()
        header.setDefaultSectionSize(10)
        header.setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)

        self.setModel(model)

    def a_update(self):
        self.setModel(_TableModel(self._data))

    def a_remove_all_items(self):
        self._data  = {}
        self.a_update()

    def a_add_items(self, items):
        self._data.update(items)