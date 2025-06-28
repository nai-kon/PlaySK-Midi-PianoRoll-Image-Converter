import customtkinter as ctk

from roll_viewer import RollViewer
from midi_to_image import Midi2Image

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

class MainFrame():
    def __init__(self, parent):
        self.parent = parent
        self.create_sidebar()
        self.roll_viewer: RollViewer | None = None
        self.midi2image = Midi2Image()

    def convert(self):
        self.midi2image.convert("Hits of the Day 16, Milne 11-1933 AB e.mid")
        self.roll_viewer = RollViewer(self.parent, 1000, 900, self.midi2image.out_img)

    def create_sidebar(self):
        sidebar = ctk.CTkScrollableFrame(self.parent, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(sidebar, text="Tracker Bar").grid(row=0, column=0, sticky="w")
        ctk.CTkOptionMenu(sidebar, values=["88-Note", "Ampico A/B", "Duo-Art"]).grid(row=1, column=0)

        ctk.CTkLabel(sidebar, text="Tempo").grid(row=2, column=0, sticky="w")
        obj = ctk.CTkSlider(sidebar, from_=30, to=140, number_of_steps=5)
        obj.set(80)
        obj.grid(row=3, column=0)
        
        obj = ctk.CTkSwitch(sidebar, text="Compensate Acceleration")
        obj.select()
        obj.grid(row=4, column=0)

        ctk.CTkLabel(sidebar, text="Acceleration rate (%/feet)").grid(row=5, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.2")
        obj.grid(row=6, column=0)

        ctk.CTkLabel(sidebar, text="Roll width (inch)").grid(row=7, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "11.25")
        obj.grid(row=8, column=0)

        ctk.CTkLabel(sidebar, text="Leftest Hole Center from Left Roll Edge (inch)").grid(row=9, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.14")
        obj.grid(row=10, column=0)

        ctk.CTkLabel(sidebar, text="Rightest Hole Center from Left Roll Edge (inch)").grid(row=11, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.14")
        obj.grid(row=12, column=0)

        ctk.CTkLabel(sidebar, text="Padding on roll start (inch)").grid(row=13, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "2.0")
        obj.grid(row=14, column=0)

        ctk.CTkLabel(sidebar, text="Padding on roll end (inch)").grid(row=15, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "2.0")
        obj.grid(row=16, column=0)

        ctk.CTkLabel(sidebar, text="Margins on roll sides (inch)").grid(row=17, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.25")
        obj.grid(row=18, column=0)

        ctk.CTkLabel(sidebar, text="Hole width (inch)").grid(row=19, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.07")
        obj.grid(row=20, column=0)

        ctk.CTkLabel(sidebar, text="Chain Perforation Gap (inch)").grid(row=21, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.0035")
        obj.grid(row=22, column=0)

        ctk.CTkLabel(sidebar, text="Chain Perforation Gap (inch)").grid(row=23, column=0, sticky="w")
        obj = MyCTkFloatInput(sidebar)
        obj.insert(0, "0.0035")
        obj.grid(row=24, column=0)

        cnv_btn = ctk.CTkButton(sidebar, text="Convert", command=self.convert)
        cnv_btn.grid(row=25, column=0, sticky="w")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("PlaySK Midi to Roll Image Converter")
    app.geometry("1400x900")
    app.iconbitmap("PlaySK_icon.ico")
    app.grid_columnconfigure(0, weight=1)  # Sidebar
    app.grid_columnconfigure(1, weight=10)
    app.grid_rowconfigure(0, weight=1)

    MainFrame(app)
    

    app.mainloop()