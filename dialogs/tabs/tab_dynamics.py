# tab_dynamics - вкладка с анализом динамики рынка

from PyQt5.QtWidgets            import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from classes.storage_manager    import StorageManager
from controls.table_widget      import TableView, TableModel
from clients.abstract.interval  import AbstractInterval, IntervalIndex
import datetime
import asyncio
import sys


class EnumCandles(AbstractInterval):
    i5      = (0, "5 шт",  5)
    i10     = (1, "10 шт", 10)
    i15     = (2, "15 шт", 15)
    i30     = (3, "30 шт", 30)
    ALL     = (4, "Все",   sys.maxsize)

class TabDynamics(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager   = manager

        self._label1    = QLabel()
        self._combobox1 = QComboBox()                           # Временной промежуток
        self._combobox2 = QComboBox()                           # Количество свечей
        self._button    = QPushButton()                         # Кнопка обновления результатов
        self._table     = TableView(self)                       # Таблица

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        self._button.setText("Обновить")
        self._label1.setText("Временной промежуток:")
        self._combobox1.addItems([e.get(IntervalIndex.DESCRIPTION) for e in self._manager.client.intervals()])
        self._combobox2.addItems([e.get(IntervalIndex.DESCRIPTION) for e in EnumCandles])
        self._combobox1.setCurrentIndex(10)
        self._combobox2.setCurrentIndex(4)

        self._combobox1.view().pressed.connect(self.refresh)                                                            # type: ignore
        self._combobox2.view().pressed.connect(self.refresh)                                                            # type: ignore
        self._button.pressed.connect(self.refresh)                                                                      # type: ignore

        self._table.setSortingEnabled(True)
        self.refresh()

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()

        grid01.addWidget(self._label1,    0, 0)
        grid01.addWidget(self._combobox1, 0, 1)
        grid01.addWidget(self._combobox2, 0, 2)
        grid01.addWidget(self._button,    0, 3)
        grid02.addWidget(self._table)

        self._label1.setFixedWidth(160)
        self._button.setFixedHeight(24)
        self._button.setFixedWidth(100)

        count  = self._combobox1.count()
        height = self._combobox1.view().sizeHintForRow(0)
        self._combobox1.view().setFixedHeight(max(200, height * count))

        layout.addLayout(grid01, 0, 0)
        layout.addLayout(grid02, 1, 0)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def update_table(self, items, colors):
        heads = ["Наименование", "Значение"]
        model = TableModel(heads, items, colors)
        self._table.setModel(model)


    def refresh(self):
        async def _load(_instrument, _interval, _start, _end):
            data = _instrument.candles(interval, start, end)
            print(f"load: {_instrument.ticker}")
            return _instrument, data

        async def _run():
            tasks = []
            instruments = self._client.instruments(buy_available=False)
            for ticker in instruments:
                tasks += [_load(instruments[ticker], interval, start, end)]
                break
            return await asyncio.gather(*tasks)


        #interval    = self._client.intervals().cast(self._combobox1.currentIndex())
        #count       = EnumCandles.cast(self._combobox2.currentIndex()).get(IntervalIndex.COUNT)

        #end         = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=10)
        #start       = end - datetime.timedelta(minutes=min(1440, count))

        #items       = asyncio.run(_run())



        #colors      = None
        #self.update_table(items, colors)


