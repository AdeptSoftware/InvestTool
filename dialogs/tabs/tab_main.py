# tab_main - вкладка с информацией об определенном инструменте
from PyQt5.QtWidgets            import QWidget, QGridLayout
from classes.storage_manager    import StorageManager


class TabMain(QWidget):
    def __init__(self, manager : StorageManager):
        super().__init__()
        self._manager = manager

        self.init_controls()
        self.init_userinterface()

    def init_controls(self):
        pass

    def init_userinterface(self):
        layout = QGridLayout()
        grid01 = QGridLayout()
        grid02 = QGridLayout()


        layout.addLayout(grid01, 0, 0)
        layout.addLayout(grid02, 1, 0)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)