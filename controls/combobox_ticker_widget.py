# combobox_ticker_widget.py
from PyQt5.QtWidgets    import QComboBox
from PyQt5.Qt           import QPixmap, QIcon, QByteArray

class TickerComboBox(QComboBox):
    def fill(self, client):
        for ticker, instrument in sorted(client.instruments().items()):
            _bytes = instrument.icon()
            if _bytes is not None:
                pix = QPixmap()
                pix.loadFromData(QByteArray(_bytes))
                icon = QIcon(pix)
            else:
                icon = QIcon(QPixmap(160, 160))
            self.addItem(icon, f"{ticker}:\t{instrument.name}")

        count = self.count()
        if count > 0:
            height = self.view().sizeHintForRow(0)
            self.view().setFixedHeight(min(500, height * count))
            self.setCurrentIndex(0)