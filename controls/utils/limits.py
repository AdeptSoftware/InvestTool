# limits.py
from dataclasses import dataclass

@dataclass
class Limits:
    x:      int
    y:      int
    x_min:  int
    x_max:  int
    y_min:  int
    y_max:  int

    def __init__(self, x, y, x_min=0, x_max=0, y_min=0, y_max=0):
        self.x     = x
        self.y     = y
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def __repr__(self):
        return str(f"Limits: {self.x} ∈ [{self.x_min};{self.x_max}]; {self.y} ∈ [{self.y_min};{self.y_max}]")

    def __call__(self, dx, dy):
        self.x = max(min(self.x + dx, self.x_max), self.x_min)
        self.y = max(min(self.y + dy, self.y_max), self.y_min)

    def reset(self):
        self.x = 0
        self.y = 0