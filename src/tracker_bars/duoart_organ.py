import customtkinter as ctk

from config import ConfigMng
from custom_widgets import CustomScrollableFrame, MyCTkIntInput

from .base import BaseConverter


class DuoArtOrgan(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        super().__init__(conf)
        self.hole_num = 176
        self.vertial_offset = 0.25
        self.vertial_offset_px = int(self.roll_dpi * self.vertial_offset)

        self.custom_hole_offsets: dict[int, dict[str, float]] = {
            note_no + 15: {"top_offset": -self.vertial_offset_px, "bottom_offset": -self.vertial_offset_px}  for note_no in range(0, 512, 2)
        }

        self.control_change_map = {}  # not used
        self.custom_note_map = {
            # channel_no: {original_note_number: new_note_number, ...}, ...
            0: {note_no: note_no * 2 - 24 for note_no in range(127)},  # lower keyboard
            1: {note_no: note_no * 2 - 25 for note_no in range(127)},  # upper keyboard
            14: {note_no: 13 + note_no * 2 for note_no in range(0, 17)} | {note_no: 129 + note_no * 2 for note_no in range(17, 30)},  # lower control holes
            15: {note_no: 14 + note_no * 2 for note_no in range(0, 17)} | {note_no: 130 + note_no * 2 for note_no in range(17, 30)},  # upper control holes
        }
        # self.custom_note_map = {
        #     # channel_no: {original_note_number: new_note_number, ...}, ...
        #     3: {note_no: note_no * 2 - 25 for note_no in range(127)},  # lower keyboard
        #     2: {note_no: note_no * 2 - 24 for note_no in range(127)},  # upper keyboard
        #     5: {note_no: 95 + note_no for note_no in range(68, 100)} | {note_no: note_no - 21 for note_no in range(21, 68)},  # lower control holes
        # }
        self.hole_x_list = [self._get_hole_x(i) for i in range(256)]


class DuoArtOrganSetting(CustomScrollableFrame):
    def __init__(self, parent: ctk.CTk, conf: ConfigMng) -> None:
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nsew")    

        self.detailed_settings = conf.tracker_config.get("detailed_settings", {})

        row_no = 0
        col_no = 0
        for key, val in self.detailed_settings.items():
            if key == "Upper playing notes (Swell)":
                row_no = 0
                col_no = 3

            # label
            font = ctk.CTkFont(size=20)
            section = ctk.CTkLabel(self, text=key, font=font)
            section.grid(row=row_no, column=col_no, columnspan=3, padx=5, pady=(30, 10))
            row_no += 1

            # MIDI Channel
            ctk.CTkLabel(self, text="Midi Ch").grid(row=row_no, column=col_no, padx=5, pady=5)
            tmp = ctk.CTkComboBox(self, values=[str(i) for i in range(16)], width=80)
            tmp.set(val["Midi Channel"])
            tmp.grid(row=row_no, column=col_no + 1, padx=5, pady=5)
            self.detailed_settings[key]["midi_ch_edit"] = tmp
            row_no += 1

            # header
            headers = ["Hole No", "Name", "MIDI Note No"]
            for i, text in enumerate(headers):
                label = ctk.CTkLabel(self, text=text)
                label.grid(row=row_no, column=col_no + i, padx=5, pady=5)
            row_no += 1

            for hole_name, val2 in val["Holes"].items():
                # Hole No.
                hole_label = ctk.CTkLabel(self, text=str(val2["hole_no"]))
                hole_label.grid(row=row_no, column=col_no, padx=5, pady=2)

                # Name
                name_entry = ctk.CTkLabel(self, text=hole_name)
                name_entry.grid(row=row_no, column=col_no + 1, padx=5, pady=2)

                # Note Number
                tmp = MyCTkIntInput(self, width=50)
                tmp.insert(0, val2["midi_note_no"])
                tmp.grid(row=row_no, column=col_no + 2, padx=5, pady=2)
                self.detailed_settings[key]["Holes"][hole_name]["midi_noteno_edit"] = tmp
                row_no += 1

    def destroy(self):
        for key, val in self.detailed_settings.items():
            self.detailed_settings[key]["Midi Channel"] = int(val["midi_ch_edit"].get())
            self.detailed_settings[key].pop("midi_ch_edit")

            for hole_name, val2 in val["Holes"].items():
                self.detailed_settings[key]["Holes"][hole_name]["midi_note_no"] = int(val2["midi_noteno_edit"].get())
                self.detailed_settings[key]["Holes"][hole_name].pop("midi_noteno_edit")
        super().destroy()
