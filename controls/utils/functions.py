# functions.py
import math

def interpolate(y0, y1, x0, x1, x):
    """ Интерполяция данных """
    return y0 + ((y1 - y0) * ((x - x0) / (x1 - x0)))

def frange(start, end, step):
    """ Разбиение нецелочисленного интервала """
    pos  = start
    base = math.ceil(math.fabs(math.log10(math.fabs(step))))
    while (step > 0 and pos <= end) or (step < 0 and pos >= end):
        yield round(pos, base)
        pos += step