# tab_instrument - вкладка с подробной информацией об инструментах
from PyQt5.QtWidgets                import QWidget, QGridLayout, QLabel, QComboBox
from PyQt5.QtCore                   import QByteArray, Qt
from PyQt5.QtGui                    import QPixmap, QIcon
from clients.abstract_instrument    import AbstractInstrument
from clients.abstract_client        import AbstractClient
from controls.table_widget          import TableWidget


class TabInstrument(QWidget):
    def __init__(self, client : AbstractClient):
        super().__init__()
        self._client   = client
        self._tickers  = []

        self._label1   = QLabel()
        self._combobox = QComboBox()                                # Выпадающий список с инструментами
        self._table    = TableWidget(self)                            # Таблица с информацией о инструменте

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        self._label1.setText("Инструмент:")

        self._combobox.currentIndexChanged.connect(self.refresh)    # type: ignore

        if self._client:
            instruments = self._client.instruments()
            if instruments:
                self._tickers = []
                for ticker, instrument in sorted(instruments.items()):
                    self._tickers += [ ticker ]
                    icon = instrument.icon()
                    if icon is not None:
                        pix = QPixmap()
                        pix.loadFromData(QByteArray(icon))
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
        self._table.a_remove_all_items()
        self._table.a_add_items(instrument.properties())
        self._table.a_update()

    def refresh(self):
        index = self._combobox.currentIndex()
        if index != -1:
            instrument = self._client.instrument(self._tickers[index])
            self.update_table(instrument)