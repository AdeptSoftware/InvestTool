# widget.py

class AbstractWidget:
    def update(self):
        pass

    def visible(self) -> bool:
        pass