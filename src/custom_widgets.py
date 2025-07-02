
import customtkinter as ctk

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


class MyScrollableFrame(ctk.CTkScrollableFrame):
    # Auto hide vertical scroll bar when not needed
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar_border_spacing = self._apply_widget_scaling(self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width"))
        self._parent_canvas.configure(yscrollcommand=lambda top, bottom: self._auto_hide_scrollbar(top, bottom))

    def _auto_hide_scrollbar(self, top, bottom):
        if float(top) == 0 and float(bottom) == 1.0:
            self._scrollbar.grid_forget()
        else:
            self._scrollbar.grid(row=1, column=1, sticky="nsew", pady=self.scrollbar_border_spacing)

        self._scrollbar.set(top, bottom)