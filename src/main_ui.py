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

    def convert(self):
        accel_rate = float(self.accel_rate.get()) / 100 if self.compensate_accel.get() else 0
        converter = Midi2Image(
            int(self.roll_dpi.get()),
            int(self.tempo_slider.get()),
            accel_rate,
            float(self.roll_start_pad.get()),
            float(self.roll_end_pad.get()),
            float(self.roll_side_margin.get()),
            float(self.roll_width.get()),
            float(self.hole_width.get()),
            float(self.chain_perf_spacing.get()),
            float(self.single_hole_max_len.get()),
            float(self.hole_0_center.get()),
            float(self.hole_99_center.get()),
        )
        converter.convert("Hits of the Day 16, Milne 11-1933 AB e.mid")
        self.roll_viewer = RollViewer(self.parent, 900, 900, converter.out_img)

    def create_sidebar(self):
        sidebar = ctk.CTkScrollableFrame(self.parent, corner_radius=0)
        sidebar.grid(row=0, column=0, padx=(10, 10), sticky="nsew")
        ctk.CTkLabel(sidebar, text="Tracker Bar").grid(row=0, column=0, sticky="w")
        self.tracker_bar = ctk.CTkOptionMenu(sidebar, values=["88-Note", "Ampico A/B", "Duo-Art"])
        self.tracker_bar.grid(row=1, column=0, sticky="w")

        self.tempo_label = ctk.CTkLabel(sidebar, text="Tempo:80")
        self.tempo_label.grid(row=2, column=0, sticky="w")
        self.tempo_slider = ctk.CTkSlider(sidebar, from_=30, to=140, number_of_steps=(140 - 30) / 5,  # 5 step
                                          command=lambda val: self.tempo_label.configure(text=f"Tempo:{val:.0f}"))
        self.tempo_slider.set(80)
        self.tempo_slider.grid(row=3, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Output Image DPI").grid(row=4, column=0, sticky="w")
        self.roll_dpi = MyCTkIntInput(sidebar)
        self.roll_dpi.insert(0, "300")
        self.roll_dpi.grid(row=5, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Roll width (inch)").grid(row=6, column=0, sticky="w")
        self.roll_width = MyCTkFloatInput(sidebar)
        self.roll_width.insert(0, "11.25")
        self.roll_width.grid(row=7, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole 0 center position (inch)").grid(row=8, column=0, sticky="w")
        self.hole_0_center = MyCTkFloatInput(sidebar)
        self.hole_0_center.insert(0, "0.14")
        self.hole_0_center.grid(row=9, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole 99 center position (inch)").grid(row=10, column=0, sticky="w")
        self.hole_99_center = MyCTkFloatInput(sidebar)
        self.hole_99_center.insert(0, "11.11")
        self.hole_99_center.grid(row=11, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Padding on roll start (inch)").grid(row=12, column=0, sticky="w")
        self.roll_start_pad = MyCTkFloatInput(sidebar)
        self.roll_start_pad.insert(0, "2.0")
        self.roll_start_pad.grid(row=13, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Padding on roll end (inch)").grid(row=14, column=0, sticky="w")
        self.roll_end_pad = MyCTkFloatInput(sidebar)
        self.roll_end_pad.insert(0, "2.0")
        self.roll_end_pad.grid(row=15, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Margins on roll sides (inch)").grid(row=16, column=0, sticky="w")
        self.roll_side_margin = MyCTkFloatInput(sidebar)
        self.roll_side_margin.insert(0, "0.25")
        self.roll_side_margin.grid(row=17, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole width (inch)").grid(row=18, column=0, sticky="w")
        self.hole_width = MyCTkFloatInput(sidebar)
        self.hole_width.insert(0, "0.07")
        self.hole_width.grid(row=19, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Single hole max length (inch)").grid(row=20, column=0, sticky="w")
        self.single_hole_max_len = MyCTkFloatInput(sidebar)
        self.single_hole_max_len.insert(0, "0.4")
        self.single_hole_max_len.grid(row=21, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Chain hole spacing (inch)").grid(row=22, column=0, sticky="w")
        self.chain_perf_spacing = MyCTkFloatInput(sidebar)
        self.chain_perf_spacing.insert(0, "0.035")
        self.chain_perf_spacing.grid(row=23, column=0, sticky="w")

        ctk.CTkLabel(sidebar, text="Shorten hole length (px)").grid(row=24, column=0, sticky="w")
        self.shorten_len = MyCTkIntInput(sidebar)
        self.shorten_len.insert(0, "10")
        self.shorten_len.grid(row=25, column=0, sticky="w")

        self.compensate_accel = ctk.CTkSwitch(sidebar, text="Compensate Acceleration")
        self.compensate_accel.select()
        self.compensate_accel.grid(row=26, column=0, sticky="w")

        self.acceleration_rate_label = ctk.CTkLabel(sidebar, text="Roll acceleration rate (%/feet)")
        self.acceleration_rate_label.grid(row=27, column=0, padx=15, sticky="w")
        self.accel_rate = MyCTkFloatInput(sidebar)
        self.accel_rate.insert(0, "0.2")
        self.accel_rate.grid(row=28, column=0, padx=15, sticky="w")

        cnv_btn = ctk.CTkButton(sidebar, text="Convert", command=self.convert)
        cnv_btn.grid(row=29, column=0, sticky="w")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("PlaySK Midi to Roll Image Converter")
    app.geometry("1400x900")
    app.iconbitmap("PlaySK_icon.ico")
    app.grid_columnconfigure(0, weight=0)  # Sidebar
    app.grid_columnconfigure(1, weight=10)
    app.grid_rowconfigure(0, weight=1)

    MainFrame(app)
    

    app.mainloop()