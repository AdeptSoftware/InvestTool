# tab_instrument - вкладка с подробной информацией об инструментах
from PyQt5.QtWidgets                    import QWidget, QGridLayout, QLabel
from controls.combobox_ticker_widget    import TickerComboBox
from clients.abstract.instrument        import AbstractInstrument
from classes.storage_manager            import StorageManager
from controls.table_widget              import TableView, TableModel


class TabInstrument(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager  = manager

        self._label1   = QLabel()
        self._combobox = TickerComboBox()                           # Выпадающий список с инструментами
        self._table    = TableView(self)                            # Таблица с информацией о инструменте

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        self._label1.setText("Инструмент:")
        self._table.setSortingEnabled(True)
        self._combobox.currentIndexChanged.connect(self.refresh)
        self._combobox.fill(self._manager.client)
        self.refresh()

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()

        grid01.addWidget(self._label1,   0, 0)
        grid01.addWidget(self._combobox, 0, 1)
        grid02.addWidget(self._table)

        self._label1.setFixedWidth(80)

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
            ticker = self._combobox.currentText().split(':')[0]
            instrument = self._manager.client.instrument(ticker)
            self.update_table(instrument)