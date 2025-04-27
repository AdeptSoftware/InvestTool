# signal.py
from controls.abstract.signal   import AbstractSignal
from PyQt5.QtCore               import pyqtSignal
from typing                     import Callable


class Signal(AbstractSignal):
    def __init__(self, signal: pyqtSignal, prepare_callback: Callable):
        """
        :param signal: сигнал формата pyqtSignal()
        :param prepare_callback: функция, которую вызовет другой поток перед отправкой сигнала об обновлении данных
        """
        self._callback = prepare_callback
        self._signal   = signal

    def connect(self, update_callback: Callable):
        self._signal.connect(update_callback)

    def notify(self):
        self._callback()        # обновление содержимого ЭУ в текущем стороннем потоке
        self._signal.emit()     # перерисовка ЭУ в основном потоке