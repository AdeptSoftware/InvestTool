# tab_instrument - вкладка с подробной информацией об инструментах
from PyQt5.QtWidgets                import QWidget, QGridLayout, QLabel, QComboBox
from PyQt5.QtCore                   import QByteArray
from PyQt5.QtGui                    import QPixmap, QIcon
from clients.abstract.instrument    import AbstractInstrument
from classes.storage_manager        import StorageManager
from controls.table_widget          import TableView, TableModel


class TabInstrument(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager  = manager
        self._tickers  = []

        self._label1   = QLabel()
        self._combobox = QComboBox()                                # Выпадающий список с инструментами
        self._table    = TableView(self)                            # Таблица с информацией о инструменте

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        self._label1.setText("Инструмент:")

        self._combobox.currentIndexChanged.connect(self.refresh)                                                        # type: ignore
        self._table.setSortingEnabled(True)

        instruments = self._manager.client.instruments()
        if instruments:
            self._tickers = []
            for ticker, instrument in sorted(instruments.items()):
                self._tickers.append(ticker)
                _bytes = instrument.icon()
                if _bytes is not None:
                    pix = QPixmap()
                    pix.loadFromData(QByteArray(_bytes))
                    icon = QIcon(pix)
                else:
                    icon = QIcon(QPixmap(160, 160))
                self._combobox.addItem(icon, f"{ticker}:\t{instrument.name}")
            self.update_table(instruments[self._tickers[0]])

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()

        grid01.addWidget(self._label1,   0, 0)
        grid01.addWidget(self._combobox, 0, 1)
        grid02.addWidget(self._table)

        self._label1.setFixedWidth(80)

        count  = self._combobox.count()
        height = self._combobox.view().sizeHintForRow(0)
        self._combobox.view().setFixedHeight(min(500, height * count))

        layout.addLayout(grid01, 0, 0)
        layout.addLayout(grid02, 1, 0)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def update_table(self, instrument : AbstractInstrument):
        props = instrument.properties()
        items = [list(props.keys()), list(props.values())]

        heads = ["Наименование", "Значение"]
        model = TableModel(heads, items)
        self._table.setModel(model)

    def refresh(self):
        index = self._combobox.currentIndex()
        if index != -1:
            instrument = self._manager.client.instrument(self._tickers[index])
            self.update_table(instrument)