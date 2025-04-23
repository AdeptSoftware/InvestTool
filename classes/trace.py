# trace.py
import os

def trace(callback, e):
    tb = e.__traceback__
    while tb.tb_next:
        tb = tb.tb_next
    file_name = os.path.relpath(tb.tb_frame.f_code.co_filename, os.getcwd())
    line_no = tb.tb_lineno
    print(f"Error: {file_name}:{line_no}:{str(callback)} {str(e)}")