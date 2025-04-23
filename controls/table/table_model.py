# table_model.py
from controls.abstract.context  import AbstractContext, Color, Rect, Alignment
from controls.abstract.element  import AbstractRendererElement
from controls.abstract.model    import AbstractModel, EventMethod
from dataclasses                import dataclass
from threading                  import RLock
from typing                     import List
from copy                       import copy, deepcopy
from enum                       import Enum

@dataclass
class TableItem(AbstractRendererElement):
    def __init__(self, data, color=None, background=None, alignment=Alignment.CC):
        self.data           = data
        self.color          = color
        self.background     = background
        self.rect           = None
        self.alignment      = alignment
        self.padding        = 5

@dataclass
class TableRow:
    items:          List[TableItem]
    index:          int
    order:          int
    height:         int
    border_width:   int
    border_color:   Color
    rect:           Rect
    resizable:      bool

    def __init__(self, index, height=30):
        self.items          = []                                                                                        # type: List[TableItem]
        self.index          = index
        self.order          = index
        self.height         = height
        self.border_width   = 1
        self.border_color   = None
        self.rect           = None
        self.resizable      = False

class TableHeader(AbstractRendererElement):
    width:          int
    border_width:   int
    border_color:   Color
    resizable:      bool

    def __init__(self, data, color=None, background=None, width=None, alignment=Alignment.CC):
        self.data           = data
        self.color          = color
        self.background     = background
        self.width          = width
        self.border_width   = 1
        self.border_color   = None
        self.rect           = None
        self.alignment      = alignment
        self.padding        = 5
        self.resizable      = True

class TableHeaders:
    items:          List[TableHeader]
    height:         int
    border_width:   int
    border_color:   Color
    rect:           Rect
    stretch:        bool

    def __init__(self, height=35, stretch=False):
        self.items          = []                                                                                        # type: List[TableHeader]
        self.height         = height
        self.rect           = None
        self.stretch        = stretch
        self.border_color   = None
        self.border_width   = 1


class TableModel(AbstractModel):
    def __init__(self, headers):
        self._sort_index        = -1
        self._sort_descending   = True

        self._lock              = RLock()
        self._head              = TableHeaders()
        self._rows              = []                                                                                    # type: List[TableRow]

        for obj in headers:
            self._head.items.append(TableHeader(obj))

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    @property
    def headers(self) -> TableHeaders:
        return self._head

    @property
    def rows(self) -> List[TableRow]:
        return self._rows

    def current_sorted_parameters(self) -> (int, bool):
        """
        :rtype: (int, bool)
        :return: (column_index, descending)
        """
        return self._sort_index, self._sort_descending

    def reset(self):
        self._head.clear()
        self._rows.clear()

    def clear(self):
        self._rows.clear()

    def remove(self, row_index):
        item = self._rows.pop(row_index)
        for row in self._rows:
            if row.index > item.index:
                row.index -= 1
            if row.order > item.order:
                row.order -= 1

    def append(self, items: List[TableItem]):
        """ Добавление новой строки """
        row = TableRow(len(self._rows))
        row.items.extend(items)
        self._rows.append(row)

    def append_rows(self, rows: List[List[str]]):
        for row in rows:
            r = TableRow(len(self._rows))
            for data in row:
                r.items.append(TableItem(data))
            self._rows.append(r)

    def resort(self):
        self.sort(self._sort_index, self._sort_descending)

    def sort(self, column, descending=True):
        if not self._head.items or not self._rows:
            return

        rows = sorted(self._rows, key=lambda item: item.items[column].data, reverse=descending)
        for order, row in enumerate(rows):
            self._rows[row.index].order = order

        self._sort_index        = column
        self._sort_descending   = descending

    @EventMethod
    def update(self, ctx : AbstractContext):
        right = 0
        for header in self._head.items:
            width = header.width or ctx.text_width(str(header.data))
            header.rect = ctx.create_rect(right, 0, width, self._head.height)
            right += width

        if self._head.stretch:
            client_width = ctx.rect().width
            if right < client_width:
                dx = (client_width - right) // len(self._head.items)
                for index, header in enumerate(self._head.items):
                    header.rect.left  += dx * index
                    header.rect.width += dx
                    right             += dx

        self._head.rect = ctx.create_rect(0, 0, right, self._head.height)

        y    = self._head.height
        rows = sorted(self._rows, key=lambda obj: obj.order)
        for row in rows:
            row.rect = ctx.create_rect(0, y, right, row.height)
            x = 0
            for index, item in enumerate(row.items):
                rc = self._head.items[index].rect
                item.rect = ctx.create_rect(x, y, rc.width, row.height)
                x = rc.right
            y += row.height
