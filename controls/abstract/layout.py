# layout.py
from controls.abstract.context import AbstractContext

class AbstractLayout:
    """ Абстрактный класс слоя """
    def __init__(self, ctx: AbstractContext, visible=True):
        self._visible = visible
        self._context = ctx

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = bool(value)

    def render(self):
        pass