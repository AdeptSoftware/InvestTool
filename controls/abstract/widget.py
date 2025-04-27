# widget.py

class AbstractWidget:
    def modify(self):
        """ Необходимо обновить данные """
        pass

    def update(self):
        """ Необходимо перерисовать виджет """
        pass

    def visible(self) -> bool:
        pass