# element.py
from controls.abstract.context  import Rect, Color, Alignment
from dataclasses                import dataclass

@dataclass
class AbstractRendererElement:
    data:           object
    color:          Color
    background:     Color
    rect:           Rect
    alignment:      Alignment
    padding:        int