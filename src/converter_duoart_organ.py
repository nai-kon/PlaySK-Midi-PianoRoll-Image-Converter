import customtkinter as ctk
from PIL import Image, ImageDraw

from config import ConfigMng
from converter_base import BaseConverter
from custom_widgets import CustomScrollableFrame, MyCTkIntInput


class DuoArtOrgan(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        self.roll_dpi = conf.tracker_config["dpi"]
        self.roll_tempo = conf.tracker_config["tempo"]
        self.roll_accelerate_rate_ft = float(conf.tracker_config["accel_rate"]) / 100 if conf.tracker_config["compensate_accel"] else 0

        # roll_width = 15.25
        # in inches
        self.roll_start_pad = 2
        self.roll_end_pad = 2
        self.roll_margin = conf.tracker_config["roll_side_margin"]
        self.hole_width = conf.tracker_config["hole_width  # 0.053333 inch"]
        self.chain_hole_spacing = conf.tracker_config["chain_perf_spacing"]
        self.single_hole_max_len = conf.tracker_config["single_hole_max_len"]
        self.leftest_hole_center = conf.tracker_config["leftest_hole_center "] # 0.346666 inch
        self.rightest_hole_center = conf.tracker_config["roll_width"] - conf.tracker_config["rightest_hole_center"]  # 0.346666 inch
        self.vertial_offset = 0.25  
        self.hole_num = 176
        self.roll_color = 120  # in grayscale

        # in pixels
        self.roll_start_pad_px = int(self.roll_dpi * self.roll_start_pad)
        self.roll_end_pad_px = int(self.roll_dpi * self.roll_end_pad)
        self.roll_margin_px = int(self.roll_dpi * self.roll_margin)
        self.roll_width_px = int(self.roll_dpi * conf.tracker_config["roll_width"])
        self.hole_width_px = int(self.roll_dpi * self.hole_width)
        self.chain_perforation_spacing_px = int(self.roll_dpi * self.chain_hole_spacing)
        self.single_hole_max_len_px = int(self.roll_dpi * self.single_hole_max_len)
        self.vertial_offset_px = int(self.roll_dpi * self.vertial_offset)
        self.shorten_hole_px = conf.tracker_config["shorten_len"]

        self.custom_hole_offsets: dict[int, dict[str, float]] = {
            note_no + 15: {"top_offset": -self.vertial_offset_px, "bottom_offset": -self.vertial_offset_px}  for note_no in range(0, 512, 2)
        }

        self.control_change_map = {}
        # self.custom_note_map = {
        #     # channel_no: {original_note_number: new_note_number, ...}, ...
        #     0: {note_no: note_no * 2 - 24 for note_no in range(127)},  # lower keyboard
        #     1: {note_no: note_no * 2 - 25 for note_no in range(127)},  # upper keyboard
        #     14: {note_no: 13 + note_no * 2 for note_no in range(0, 17)} | {note_no: 129 + note_no * 2 for note_no in range(17, 30)},  # lower control holes
        #     15: {note_no: 14 + note_no * 2 for note_no in range(0, 17)} | {note_no: 130 + note_no * 2 for note_no in range(17, 30)},  # upper control holes
        # }
        self.custom_note_map = {
            # channel_no: {original_note_number: new_note_number, ...}, ...
            3: {note_no: note_no * 2 - 25 for note_no in range(127)},  # lower keyboard
            2: {note_no: note_no * 2 - 24 for note_no in range(127)},  # upper keyboard
            5: {note_no: 95 + note_no for note_no in range(68, 100)} | {note_no: note_no - 21 for note_no in range(21, 68)},  # lower control holes
        }
        self.hole_x_list = [self._get_hole_x(i) for i in range(512)]
        self.out_img: Image.Image | None = None
        self.draw: ImageDraw | None = None


class DuoArtOrganSetting:
    def __init__(self, parent: ctk.CTk, conf: ConfigMng) -> None:
        self.dialog = CustomScrollableFrame(parent, fg_color=("#CCCCCC", "#111111"))
        self.dialog.grid(row=0, column=0, sticky="nsew")    

        self.control_configs = conf.tracker_config.get("controls", {})

        row_no = 0
        col_no = 0
        for key, val in self.control_configs.items():
            if key == "Upper playing notes (Swell)":
                row_no = 0
                col_no = 3

            # label
            font = ctk.CTkFont(size=20)
            section = ctk.CTkLabel(self.dialog, text=key, font=font)
            section.grid(row=row_no, column=col_no, columnspan=3, padx=5, pady=(30, 10))
            row_no += 1

            # MIDI Channel
            ctk.CTkLabel(self.dialog, text="Midi Ch").grid(row=row_no, column=col_no, padx=5, pady=5)
            tmp = ctk.CTkComboBox(self.dialog, values=[str(i) for i in range(16)], width=80)
            tmp.set(val["Midi Channel"])
            tmp.grid(row=row_no, column=col_no + 1, padx=5, pady=5)
            self.control_configs[key]["Midi Channel"] = tmp
            row_no += 1

            # header
            headers = ["Hole No", "Name", "MIDI Note No"]
            for i, text in enumerate(headers):
                label = ctk.CTkLabel(self.dialog, text=text)
                label.grid(row=row_no, column=col_no + i, padx=5, pady=5)
            row_no += 1

            for hole_name, val2 in val["Holes"].items():
                # Hole No.
                hole_label = ctk.CTkLabel(self.dialog, text=str(val2["hole_no"]))
                hole_label.grid(row=row_no, column=col_no, padx=5, pady=2)

                # Name
                name_entry = ctk.CTkLabel(self.dialog, text=hole_name)
                name_entry.grid(row=row_no, column=col_no + 1, padx=5, pady=2)

                # Note Number
                tmp = MyCTkIntInput(self.dialog, width=50)
                tmp.insert(0, val2["midi_note_no"])
                tmp.grid(row=row_no, column=col_no + 2, padx=5, pady=2)
                self.control_configs[key]["Holes"][hole_name]["midi_note_no_edit"] = tmp

                row_no += 1

        dark_mode_btn = ctk.CTkButton(self.dialog, text="commit", width=20, command=self.debug)
        dark_mode_btn.grid(row=row_no, column=0, padx=5, pady=5)

    def debug(self):
        # debug
        for row_pos, val in self.control_configs.items():
            for hole_name, val2 in val["Holes"].items():
                print(hole_name, val2["midi_note_no_edit"].get())


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("650x600")

    app.grid_columnconfigure(0, weight=1)  #
    app.grid_rowconfigure(0, weight=1)

    conf = ConfigMng()
    conf.load_tracker_config("Aeolian 176-note")

    DuoArtOrganSetting(app, conf)


    app.mainloop()