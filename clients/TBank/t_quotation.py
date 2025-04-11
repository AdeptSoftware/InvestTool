# t_quotation.py
from tinkoff.invest import Quotation

class TQuotation(float):
    def __new__(cls, q):
        if isinstance(q, Quotation):
            value = q.units + (q.nano / 1e9)
            value = round(value, 8) if abs(value) >= 1e-10 else value                                                   # 0.869999999999 -> 0.87
            instance = super().__new__(cls, value)
            instance.units = q.units
            instance.nano  = q.nano
            return instance
        return super().__new__(cls, q)