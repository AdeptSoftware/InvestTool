from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore    import QAbstractTableModel, Qt
from PyQt5.QtGui     import QColor
from enum            import Enum, IntEnum

class TableModel(QAbstractTableModel):
    def __init__(self, headers, data, txt_colors=None, bkg_colors=None):
        super().__init__()
        self._headers    = headers
        self._data       = data
        self._txt_colors = txt_colors
        self._bkg_colors = bkg_colors

    def rowCount(self, parent=None):
        return len(self._data[0]) if self._data else 0

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        if col >= len(self._data):
            return None

        match role:
            case Qt.DisplayRole | Qt.EditRole:
                return self._data[col][row]
            case Qt.ForegroundRole:
                if self._txt_colors:
                    return QColor(self._txt_colors[col][row])
                return QColor(255, 255, 255)
            case Qt.BackgroundRole:
                if self._bkg_colors:
                    return QColor(self._bkg_colors[col][row])
                return QColor(28, 28, 28)

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]

        return f"{section}"

    def sort(self, column, order=Qt.AscendingOrder):
        if not self._data or len(self._data[0]) == 0:
            return

        self.layoutAboutToBeChanged.emit()

        cnt        = len(self._data[0])
        rows       = list(zip(*self._data))
        txt_colors = list(zip(*self._txt_colors)) if self._txt_colors else None
        bkg_colors = list(zip(*self._bkg_colors)) if self._bkg_colors else None

        combined   = list(zip(rows, txt_colors or [None]*cnt, bkg_colors or [None]*cnt))

        combined.sort(
            key=lambda x: x[0][column] if column < len(x[0]) else "",
            reverse=(order == Qt.DescendingOrder),
        )

        sorted_rows, sorted_txt, sorted_bkg = zip(*combined)

        self._data = [ list(col) for col in zip(*sorted_rows) ]
        if self._txt_colors:
            self._txt_colors = [ list(col) for col in zip(*sorted_txt) ]
        if self._bkg_colors:
            self._bkg_colors = [ list(col) for col in zip(*sorted_bkg) ]

        self.layoutChanged.emit()

    def set(self, data, txt_colors=None, bkg_colors=None):
        self.layoutAboutToBeChanged.emit()
        self._txt_colors = txt_colors
        self._bkg_colors = bkg_colors
        self._data       = data
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
                background-color:   #1C1C1C;
                color:              white;
                padding:            1px;
                margin:             0px
            }
            QTableWidget::item {
                padding:            1px;
                margin:             0px;
            }
            QHeaderView::up-arrow, QHeaderView::down-arrow {
                image:              url(none);
            }
            """)

        header = self.verticalHeader()
        header.setDefaultSectionSize(10)
        header.setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)

    def set(self, data, txt_colors=None, bkg_colors=None):
        self.model().set(data, txt_colors, bkg_colors)
