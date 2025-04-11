from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore    import QAbstractTableModel, Qt
from PyQt5.QtGui     import QColor
from enum            import Enum, IntEnum

class TableModel(QAbstractTableModel):
    def __init__(self, headers, data, txt_colors=None, bkg_colors=None):
        super().__init__()
        self._data          = data
        self._headers       = headers
        self._txt_colors    = txt_colors
        self._bkg_colors    = bkg_colors

    def rowCount(self, parent=None):
        if self._data:
            return len(self._data[0])
        return 0

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        if col >= len(self._data):
            return None

        match role:
            case Qt.DisplayRole:
                return self._data[col][row]
            case Qt.ForegroundRole:
                if self._txt_colors:
                    return QColor(self._txt_colors[col][row])
            case Qt.BackgroundRole:
                if self._bkg_colors:
                    return QColor(self._bkg_colors[col][row])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        match orientation:
            case Qt.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
        return f"{section}"

    def sort(self, column, order=None):
        if self._data:
            self.layoutAboutToBeChanged.emit()

            empty = []
            if not self._txt_colors or not self._bkg_colors:
                for i in range(len(self._data)):
                    empty += [[0]*len(self._data[i])]

            p = [ list(zip(*self._data)),
                  list(zip(*(self._txt_colors or empty))),
                  list(zip(*(self._bkg_colors or empty))) ]

            combined = list(zip(*p))
            combined.sort(
                key=lambda x: x[0][column] if column < len(x[0]) else "",
                reverse=(order == Qt.DescendingOrder),
            )

            index = 0
            for _list in zip(*combined):
                p[index] = [ list(col) for col in zip(*_list) ]
                index += 1

            self._data       = p[0]
            self._txt_colors = (self._txt_colors and p[1]) or self._txt_colors
            self._bkg_colors = (self._bkg_colors and p[2]) or self._bkg_colors

            self.layoutChanged.emit()

class TableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
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

        header = self.verticalHeader()
        header.setDefaultSectionSize(10)
        header.setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)