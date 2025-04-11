# main_window.py
from PyQt5.QtWidgets                import QTabWidget, QVBoxLayout
from dialogs.base_dialog            import Dialog
from clients.TBank.t_client         import TClient
from classes.storage_manager        import StorageManager
from dialogs.tabs.tab_main          import *
from dialogs.tabs.tab_instrument    import *
from dialogs.tabs.tab_price         import *
from dialogs.tabs.tab_dynamics      import *


class MainWindow(Dialog):
    def __init__(self):
        super().__init__()
        self._mngr = StorageManager(self._client("token.ini"))

        self._tabs = QTabWidget()
        self._tabs.addTab(TabMain(self._mngr),       "Главная")
        self._tabs.addTab(TabInstrument(self._mngr), "Инструменты")
        self._tabs.addTab(TabPrice(self._mngr),      "Курс")
        self._tabs.addTab(TabDynamics(self._mngr),   "Динамика цен")

        self._tabs.currentChanged.connect(self.on_tab_change)
        self._tabs.setCurrentIndex(3)

        self._mngr.client.reconnect()

        layout = QVBoxLayout()
        layout.addWidget(self._tabs)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

        self.setGeometry(0, 0, 1000, 500)
        self.setWindowTitle("InvestTool")
        self.show()

    @staticmethod
    def _client(filename):
        with open(filename, 'r') as f:
            return TClient(token=f.read())

    def on_tab_change(self, index):
        widget = self._tabs.widget(index)
        if isinstance(widget, TabPrice):
            widget.set_chart_focus()
            widget.update()