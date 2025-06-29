import os

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
from tkinterdnd2 import DND_ALL, TkinterDnD

from midi_to_image import Midi2Image
from roll_viewer import RollViewer

APP_TITLE = "PlaySK Midi to Roll Image Converter"

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
class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class MainFrame():
    def __init__(self, parent) -> None:
        self.parent = parent
        self.create_sidebar()
        self.roll_viewer: RollViewer | None = None
        self.midi_file_path = None
        self.is_dark_mode = True

    def change_dark_light_mode(self) -> None:
        self.is_dark_mode = not self.is_dark_mode
        ctk.set_appearance_mode("Dark" if self.is_dark_mode else "Light")

    def convert(self) -> None:
        if self.midi_file_path is None:
            return

        accel_rate = float(self.accel_rate.get()) / 100 if self.compensate_accel.get() else 0
        converter = Midi2Image(
            int(self.roll_dpi.get()),
            int(self.tempo_slider.get()),
            accel_rate,
            float(self.roll_side_margin.get()),
            float(self.roll_width.get()),
            float(self.hole_width.get()),
            float(self.chain_perf_spacing.get()),
            float(self.single_hole_max_len.get()),
            float(self.hole_0_center.get()),
            float(self.hole_99_center.get()),
            int(self.shorten_len.get()),
            # float(self.roll_start_pad.get()),
            # float(self.roll_end_pad.get()),
        )
        converter.convert(self.midi_file_path)
        if isinstance(self.roll_viewer, RollViewer):
            self.roll_viewer.set_image(converter.out_img)
        else:
            self.roll_viewer = RollViewer(self.parent, 900, 900, converter.out_img)
    
    def _open_file(self, path):
        print(path)
        self.midi_file_path = path
        # change app title
        name = os.path.basename(self.midi_file_path)
        self.parent.title(APP_TITLE + " - " + name)
        self.convert() 

    def file_sel(self):
        if path:= ctk.filedialog.askopenfilename(title="Select a MIDI file", filetypes=[("MIDI file", "*.mid")]):
            self._open_file(path)

    def drop_file(self, event):
        paths: tuple[str] = self.parent.tk.splitlist(event.data)  # parse filepath list
        path = paths[0]  # only one file is supported
        if not path.endswith(".mid"):
            CTkMessagebox(icon="icons/warning_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png", title="Unsupported File", message="Not MIDI file")
        else:
            self._open_file(path)

    def save_image(self):
        if self.midi_file_path is None:
            return

        name = os.path.basename(self.midi_file_path)
        default_savename = os.path.splitext(name)[0] + f" tempo{self.tempo_slider.get()}.png"
        if path:= ctk.filedialog.asksaveasfilename(title="Save Converted Image", initialfile=default_savename, filetypes=[("PNG file", "*.png")]):
            dpi = int(self.roll_dpi.get())
            self.roll_viewer.image.save(path, dpi=(dpi, dpi))

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.parent, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")

        btnimg = ctk.CTkImage(Image.open("icons/folder_open_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(25, 25))
        self.fileopen = ctk.CTkButton(sidebar, text="Open & Convert MIDI", image=btnimg, command=self.file_sel)
        self.fileopen.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(sidebar, text="Tracker Bar").grid(row=1, padx=10, column=0, sticky="w")
        self.tracker_bar = ctk.CTkOptionMenu(sidebar, values=["88-Note", "Ampico A/B", "Duo-Art"])
        self.tracker_bar.grid(row=2, column=0, padx=10, sticky="w")

        self.tempo_label = ctk.CTkLabel(sidebar, text="Tempo:80")
        self.tempo_label.grid(row=3, column=0, padx=10, sticky="w")
        self.tempo_slider = ctk.CTkSlider(sidebar, from_=30, to=140, number_of_steps=(140 - 30) / 5,  # 5 step
                                          command=lambda val: self.tempo_label.configure(text=f"Tempo:{val:.0f}"))
        self.tempo_slider.set(80)
        self.tempo_slider.grid(row=4, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Output Image DPI").grid(row=5, column=0, padx=10, sticky="w")
        self.roll_dpi = MyCTkIntInput(sidebar)
        self.roll_dpi.insert(0, "300")
        self.roll_dpi.grid(row=6, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Roll width (inch)").grid(row=7, column=0, padx=10, sticky="w")
        self.roll_width = MyCTkFloatInput(sidebar)
        self.roll_width.insert(0, "11.25")
        self.roll_width.grid(row=8, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole 0 center position (inch)").grid(row=9, column=0, padx=10, sticky="w")
        self.hole_0_center = MyCTkFloatInput(sidebar)
        self.hole_0_center.insert(0, "0.14")
        self.hole_0_center.grid(row=10, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole 99 center position (inch)").grid(row=11, column=0, padx=10, sticky="w")
        self.hole_99_center = MyCTkFloatInput(sidebar)
        self.hole_99_center.insert(0, "11.11")
        self.hole_99_center.grid(row=12, column=0, padx=10, sticky="w")

        # ctk.CTkLabel(sidebar, text="Padding on roll start (inch)").grid(row=13, column=0, padx=10, sticky="w")
        # self.roll_start_pad = MyCTkFloatInput(sidebar)
        # self.roll_start_pad.insert(0, "2.0")
        # self.roll_start_pad.grid(row=14, column=0, padx=10, sticky="w")

        # ctk.CTkLabel(sidebar, text="Padding on roll end (inch)").grid(row=15, column=0, padx=10, sticky="w")
        # self.roll_end_pad = MyCTkFloatInput(sidebar)
        # self.roll_end_pad.insert(0, "2.0")
        # self.roll_end_pad.grid(row=16, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Margins on roll sides (inch)").grid(row=17, column=0, padx=10, sticky="w")
        self.roll_side_margin = MyCTkFloatInput(sidebar)
        self.roll_side_margin.insert(0, "0.25")
        self.roll_side_margin.grid(row=18, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Hole width (inch)").grid(row=19, column=0, padx=10, sticky="w")
        self.hole_width = MyCTkFloatInput(sidebar)
        self.hole_width.insert(0, "0.07")
        self.hole_width.grid(row=20, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Single hole max length (inch)").grid(row=21, column=0, padx=10, sticky="w")
        self.single_hole_max_len = MyCTkFloatInput(sidebar)
        self.single_hole_max_len.insert(0, "0.4")
        self.single_hole_max_len.grid(row=22, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Chain hole spacing (inch)").grid(row=23, column=0, padx=10, sticky="w")
        self.chain_perf_spacing = MyCTkFloatInput(sidebar)
        self.chain_perf_spacing.insert(0, "0.035")
        self.chain_perf_spacing.grid(row=24, column=0, padx=10, sticky="w")

        ctk.CTkLabel(sidebar, text="Shorten hole length (px)").grid(row=25, column=0, padx=10, sticky="w")
        self.shorten_len = MyCTkIntInput(sidebar)
        self.shorten_len.insert(0, "10")
        self.shorten_len.grid(row=26, column=0, padx=10, sticky="w")

        self.compensate_accel = ctk.CTkSwitch(sidebar, text="Compensate Acceleration")
        self.compensate_accel.select()
        self.compensate_accel.grid(row=27, column=0, padx=10, sticky="w")

        self.acceleration_rate_label = ctk.CTkLabel(sidebar, text="Acceleration rate (%/feet)")
        self.acceleration_rate_label.grid(row=28, column=0, padx=25, sticky="w")
        self.accel_rate = MyCTkFloatInput(sidebar)
        self.accel_rate.insert(0, "0.2")
        self.accel_rate.grid(row=29, column=0, padx=25, sticky="w")

        btnimg = ctk.CTkImage(Image.open("icons/refresh_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(25, 25))
        cnv_btn = ctk.CTkButton(sidebar, text="Update", image=btnimg, command=self.convert)
        cnv_btn.grid(row=30, column=0, padx=10, pady=10, sticky="ew")

        btnimg = ctk.CTkImage(Image.open("icons/download_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(25, 25))
        save_btn = ctk.CTkButton(sidebar, text="Save Image", image=btnimg, command=self.save_image)
        save_btn.grid(row=31, column=0, padx=10, pady=10, sticky="ew")

        btnimg = ctk.CTkImage(light_image=Image.open("icons/dark_mode_256dp_1F1F1F_FILL0_wght400_GRAD0_opsz48.png"),
                                        dark_image=Image.open("icons/light_mode_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(20, 20))
        dark_mode_btn = ctk.CTkButton(sidebar, text="", width=20, fg_color="transparent", hover_color=("gray70", "gray30"), image=btnimg, command=self.change_dark_light_mode)
        dark_mode_btn.grid(row=32, column=0, padx=10, sticky="sw")

if __name__ == "__main__":
    app = Tk()
    app.title(APP_TITLE)
    app.geometry("1200x900")
    app.iconbitmap("icons/PlaySK_icon.ico")
    app.grid_columnconfigure(0, weight=0)  # Sidebar
    app.grid_columnconfigure(1, weight=10)
    app.grid_rowconfigure(0, weight=1)

    mainframe = MainFrame(app)

    app.drop_target_register(DND_ALL)
    app.dnd_bind("<<Drop>>", lambda e: mainframe.drop_file(e))

    

    app.mainloop()