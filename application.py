import sys
from dialogs.main_window import MainWindow
from PyQt5.QtWidgets    import QApplication
from PyQt5.QtCore       import QPoint

class Application:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._wnd = MainWindow()

        self.center(self._wnd)

        self._app.setStyleSheet('''
            QLineEdit {
                border-width: 1px;
                border-style: solid;
                border-color: rgb(209, 209, 210);
            }
            QLineEdit:focus {
                border-color: rgb(0, 128, 255);
            }
        ''')

        sys.exit(self._app.exec_())

    def center(self, wnd):
        scr_rect = self._app.desktop().screenGeometry()
        wnd_size = wnd.size()
        wnd.move(QPoint(int((scr_rect.width()-wnd_size.width())/2),
                        int((scr_rect.height()-wnd_size.height())/2)))