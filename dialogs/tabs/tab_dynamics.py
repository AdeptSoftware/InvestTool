# tab_dynamics - вкладка с анализом динамики рынка
from PyQt5.QtWidgets            import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from clients.abstract_client    import AbstractClient
from controls.table_widget        import TableWidget
from enum                       import Enum

class EnumTuple(Enum):
    @classmethod
    def cast(cls, index):
        for item in cls:
            if item.value[0] == index:
                return item
        raise ValueError(f"Элемента {cls.__name__} с индексом {index} не существует!")

class EnumIntervals(EnumTuple):
    i30S    = (0,  "30c")
    i1M     = (1,  "1м")
    i5M     = (2,  "5м")
    i10M    = (3,  "10м")
    i30M    = (4,  "30м")
    i1H     = (5,  "1ч")
    i3H     = (6,  "3ч")
    i6H     = (7,  "6ч")
    i12H    = (8,  "12ч")
    i1D     = (9,  "1д")
    i7D     = (10, "7д")
    i30D    = (11, "30д")
    i365D   = (12, "365д")

class EnumCandles(EnumTuple):
    i5      = (0, 5,  "5 шт")
    i10     = (1, 10, "10 шт")
    i15     = (2, 15, "15 шт")
    i30     = (3, 30, "30 шт")
    ALL     = (4, 0,  "Все")

class TabDynamics(QWidget):
    def __init__(self, client : AbstractClient):
        super().__init__()
        self._client    = client

        self._label1    = QLabel()
        self._combobox1 = QComboBox()                           # Временной промежуток
        self._combobox2 = QComboBox()                           # Количество свечей
        self._button    = QPushButton()                         # Кнопка обновления результатов
        self._table     = TableWidget(self)                       # Список

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        self._button.setText("Обновить")
        self._label1.setText("Временной промежуток:")
        self._combobox1.addItems([e.value[1] for e in EnumIntervals])
        self._combobox2.addItems([e.value[2] for e in EnumCandles])
        self._combobox1.setCurrentIndex(4)
        self._combobox2.setCurrentIndex(3)

        self._combobox1.view().pressed.connect(self.refresh)    # type: ignore
        self._combobox2.view().pressed.connect(self.refresh)    # type: ignore
        self._button.pressed.connect(self.refresh)              # type: ignore

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

    def refresh(self):
        interval = EnumIntervals.cast(self._combobox1.currentIndex())
        count    = EnumCandles.cast(self._combobox2.currentIndex()).value[1]

        # data     = self._api.tickers(interval, count)
        pass


