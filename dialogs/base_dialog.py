# base_dialog - базовый класс диалога
from PyQt5.QtWidgets                import QAction, QPushButton, QDialog
from PyQt5.QtGui                    import QIcon

class Dialog(QDialog):
    def _add_submenu(self, menu, title, method, icon: QIcon = None, shortcut=None, tip=None):
        if icon:
            action = QAction(icon, title, self)
        else:
            action = QAction(title, self)
        action.setShortcut(shortcut or "")
        action.setStatusTip(tip or "")
        action.triggered.connect(method)
        menu.addAction(action)

    def _add_button(self, title, method) -> QPushButton:
        button = QPushButton(title, self)
        button.clicked.connect(method)
        return button

