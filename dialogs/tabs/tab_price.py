# tab_main - вкладка с информацией о курсе инструмента
from PyQt5.QtWidgets             import QWidget, QGridLayout, QLabel, QComboBox
from PyQt5.QtCore                import QByteArray
from PyQt5.QtGui                 import QPixmap, QIcon

from classes.storage_manager     import StorageManager, Storage

from clients.abstract.client     import SubscriptionType
from clients.abstract.interval   import IntervalIndex
from clients.abstract.instrument import AbstractInstrument

from controls.orderbook_widget   import OrderBookWidget
from controls.chart_widget       import ChartWidget

class TabPrice(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager           = manager
        self._tickers           = []

        self._label1            = QLabel()
        self._label2            = QLabel()
        self._combobox_ticker   = QComboBox()
        self._combobox_interval = QComboBox()
        self._chart             = ChartWidget(self)
        self._orderbook         = OrderBookWidget(self)

        self.init_controls()
        self.init_userinterface()

    def set_chart_focus(self):
        self._chart.setFocus()

    def init_controls(self):
        self._label1.setText("Инструмент:")

        self._combobox_ticker.currentIndexChanged.connect(self.refresh)         # type: ignore
        self._combobox_interval.currentIndexChanged.connect(self.refresh)       # type: ignore

        items = [ e.get(IntervalIndex.DESCRIPTION) for e in self._manager.client.intervals() ]
        self._combobox_interval.addItems(items)

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
                self._combobox_ticker.addItem(icon, f"{ticker}:\t{instrument.name}")
            self.change_instrument(self._tickers[0], True)

        self._combobox_ticker.setCurrentIndex(136)
        self._combobox_interval.setCurrentIndex(0)

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()

        grid01.addWidget(self._label1,              0, 0)
        grid01.addWidget(self._combobox_ticker,     0, 1)
        grid01.addWidget(self._combobox_interval,   0, 2)
        grid02.addWidget(self._chart,               0, 0)
        grid02.addWidget(self._orderbook,           0, 1)

        self._label1.setFixedWidth(80)
        self._combobox_interval.setFixedWidth(80)
        self._orderbook.setFixedWidth(200)

        count  = self._combobox_ticker.count()
        height = self._combobox_ticker.view().sizeHintForRow(0)
        self._combobox_ticker.view().setFixedHeight(min(500, height * count))

        layout.addLayout(grid01, 0, 0)
        layout.addLayout(grid02, 1, 0)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def change_instrument(self, ticker, init=False):
        index = self._combobox_interval.currentIndex()
        if index != -1:
            source : Storage = self._chart.view.source
            if source:
                source.detach(self._chart.update,     SubscriptionType.CANDLE)
                source.detach(self._orderbook.update, SubscriptionType.ORDERBOOK)
                source.detach(self._orderbook.update, SubscriptionType.LAST_PRICE)

            source = self._manager.get(ticker)
            if source:
                self._chart.view.source = source
                self._chart.view.reset()
                self._chart.update()

                self._orderbook.view.source = source
                self._orderbook.view.reset()
                self._orderbook.update()

                source.attach(self._chart.update,     SubscriptionType.CANDLE)
                source.attach(self._orderbook.update, SubscriptionType.ORDERBOOK)
                source.attach(self._orderbook.update, SubscriptionType.LAST_PRICE)

                if not init:
                    self._manager.client.reconnect()

    def refresh(self):
        index = self._combobox_ticker.currentIndex()
        if index != -1:
            self.change_instrument(self._tickers[index])
