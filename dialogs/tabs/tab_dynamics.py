# tab_dynamics - вкладка с анализом динамики рынка
from PyQt5.QtWidgets                    import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from controls.combobox_ticker_widget    import TickerComboBox
from controls.table_widget_ex           import TableWidgetEx, TableModel, TableItem
from clients.abstract.interval          import AbstractInterval, IntervalIndex
from classes.storage_manager            import StorageManager, SubscriptionType
from classes.analyzer                   import DataAnalyzer

import datetime
import sys


class TabDynamics(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager           = manager

        self._combobox_tickers  = TickerComboBox()              # Временной промежуток
        self._combobox_delta    = QComboBox()                   # Временной промежуток
        self._button            = QPushButton()                 # Кнопка обновления результатов
        self._table             = TableWidgetEx(self)           # Таблица

        self._updated = datetime.datetime.now()

        self.init_controls()
        self.init_userinterface()

        for storage in self._manager.items():
            storage.update.connect(self.refresh)

    def __del__(self):
        for storage in self._manager.items():
            storage.update.connect(self.refresh)

    def init_controls(self):
        self._button.setText("Отслеживать")
        self._combobox_delta.addItems([e.get(IntervalIndex.DESCRIPTION) for e in self._manager.client.intervals()])
        self._combobox_delta.setCurrentIndex(10)
        self._combobox_tickers.fill(self._manager.client)

        self._combobox_delta.view().pressed.connect(self.refresh)                                                             # type: ignore
        self._button.pressed.connect(self.refresh)                                                                      # type: ignore

        model = TableModel(["Наименование", "Цена", "Прирост", "%", "Ускорение", "R²"])
        model.headers.stretch  = True
        self._table.view.model = model

        self.refresh()

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()

        grid01.addWidget(self._combobox_tickers, 0, 0)
        grid01.addWidget(self._combobox_delta,   0, 1)
        grid01.addWidget(self._button,           0, 2)
        grid02.addWidget(self._table)

        self._button.setFixedHeight(24)
        self._button.setFixedWidth(100)
        self._combobox_delta.setFixedWidth(75)

        layout.addLayout(grid01, 0, 0)
        layout.addLayout(grid02, 1, 0)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def refresh(self):
        now = datetime.datetime.now()
        if now - self._updated < datetime.timedelta(seconds=0.1):
            return

        end = now
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        analyzer = DataAnalyzer(self._manager)
        items = [[storage.name() for storage in self._manager.items()], *analyzer.dynamic(start, end)]
        items = list(zip(*items))

        with self._table.view.model:
            model = self._table.view.model
            model.clear()
            model.append_rows(items)
            model.sort(*model.current_sorted_parameters())
            self._table.update()

        self._updated = now