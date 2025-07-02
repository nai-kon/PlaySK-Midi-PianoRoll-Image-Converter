
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD


def MyCTkFloatInput(parent):
    def validate_float_input(value):
        try:
            if value != "":  # Allow empty input
                float(value)  # Try to convert to float
            return True
        except ValueError:
            return False

    validate_cmd = parent.register(validate_float_input)
    return ctk.CTkEntry(parent, validate="key", validatecommand=(validate_cmd, "%P"))

def MyCTkIntInput(parent):
    def validate_int_input(value):
        try:
            if value != "":  # Allow empty input
                int(value)  # Try to convert to int
            return True
        except ValueError:
            return False

    validate_cmd = parent.register(validate_int_input)
    return ctk.CTkEntry(parent, validate="key", validatecommand=(validate_cmd, "%P"))


# For Drag&Drop File Support
# https://stackoverflow.com/a/75527642
class MyTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


# Auto hide vertical scroll bar when not needed
class CustomScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._parent_canvas.configure(yscrollcommand=lambda top, bottom: self._auto_hide_scrollbar(top, bottom))

    def _auto_hide_scrollbar(self, top, bottom):
        if float(top) == 0 and float(bottom) == 1.0:
            self._scrollbar.grid_remove()
        else:
            self._scrollbar.grid()

        self._scrollbar.set(top, bottom)
