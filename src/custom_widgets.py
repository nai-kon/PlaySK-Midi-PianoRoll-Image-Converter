
from typing import Any, Callable

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD


class MyCTkFloatInput(ctk.CTkEntry):
    def __init__(self, parent, on_change: Callable[[Any], None] | None = None) -> None:
        self.prev_value: str | None = None
        self.on_change = on_change
        validate_cmd = parent.register(self.validate_input)
        super().__init__(parent, validate="key", validatecommand=(validate_cmd, "%P"))
        self.bind("<Return>", command=self.on_change_inner)  # callback on Enter
        self.bind("<FocusOut>", command=self.on_change_inner)  # callback on leave input

    def insert(self, index: int, string: str | int | float) -> None:
        self.prev_value = str(string)
        super().insert(index, string)

    def on_change_inner(self, event):
        value = self.get()
        if self.on_change and value != self.prev_value:
            self.on_change(value)
        self.prev_value = value

    def validate_input(self, value):
        try:
            if value != "":  # Allow empty input
                float(value)  # Try to convert to float
            return True
        except ValueError:
            return False


class MyCTkIntInput(MyCTkFloatInput):
    def validate_input(self, value):
        try:
            if value != "":  # Allow empty input
                int(value)  # Try to convert to float
            return True
        except ValueError:
            return False


# For Drag&Drop File Support
# https://stackoverflow.com/a/75527642
class MyTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs) -> None:
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
