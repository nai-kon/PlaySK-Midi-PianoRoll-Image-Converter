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
            note_no + 15: {"top_offset": -self.vertial_offset_px, "bottom_offset": -self.vertial_offset_px}  for note_no in range(0, 256, 2)
        }

        self.control_change_map = {}  # not used
        self.custom_note_map = {}
        # map hole_no and note_no
        tracker = conf.tracker_config["detailed_settings"]
        for key in ("Lower control holes (Great)", "Upper control holes (Swell)"):
            channel = tracker[key]["Midi Channel"] - 1
            self.custom_note_map[channel] = {v["midi_note_no"]: v["hole_no"] + 15 for v in tracker[key]["Holes"].values()}
        for key in ("Lower playing 58 notes (Great)", "Upper playing 58 notes (Swell)"):
            lowest_hole_no = tracker[key]["Holes"]["Lowest Note"]["hole_no"]
            highest_hole_no = tracker[key]["Holes"]["Highest Note"]["hole_no"]
            lowest_midi_note_no = tracker[key]["Holes"]["Lowest Note"]["midi_note_no"]  # to organ note number
            midi_note_no = lowest_midi_note_no
            for hole_no in range(lowest_hole_no, highest_hole_no + 1, 2):
                channel = tracker[key]["Midi Channel"] - 1
                self.custom_note_map.setdefault(channel, {})
                self.custom_note_map[channel] |= {midi_note_no: hole_no + 15}
                midi_note_no += 1

        print(self.custom_note_map)

        # self.custom_note_map = {
        #     # channel_no: {original_note_number: new_note_number, ...}, ...
        #     0: {note_no: note_no * 2 - 24 for note_no in range(127)},  # lower keyboard
        #     1: {note_no: note_no * 2 - 25 for note_no in range(127)},  # upper keyboard
        #     14: {note_no: 13 + note_no * 2 for note_no in range(0, 17)} | {note_no: 129 + note_no * 2 for note_no in range(17, 30)},  # lower control holes
        #     15: {note_no: 14 + note_no * 2 for note_no in range(0, 17)} | {note_no: 130 + note_no * 2 for note_no in range(17, 30)},  # upper control holes
        # }
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
        self.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", anchor="nw")
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", anchor="ne")

        self.detailed_settings = conf.tracker_config.get("detailed_settings", {})

        row_no = 0
        frame = left_frame
        for key in ("Upper playing 58 notes (Swell)", "Upper control holes (Swell)",
                    "Lower playing 58 notes (Great)", "Lower control holes (Great)"):
            val = self.detailed_settings[key]
            if key == "Lower playing 58 notes (Great)":
                row_no = 0
                frame = right_frame

            # label
            font = ctk.CTkFont(size=20)
            section = ctk.CTkLabel(frame, text=key, font=font)
            section.grid(row=row_no, column=0, columnspan=3, padx=5, pady=(30, 10))
            row_no += 1

            # MIDI Channel
            ctk.CTkLabel(frame, text="Midi Ch").grid(row=row_no, column=0, padx=5, pady=5)
            tmp = ctk.CTkComboBox(frame, values=[str(i) for i in range(1, 16 + 1)], width=80)
            tmp.set(val["Midi Channel"])
            tmp.grid(row=row_no, column=1, padx=5, pady=5)
            row_no += 1
            self.detailed_settings[key]["midi_ch_edit"] = tmp

            # header
            headers = ["Hole No", "Name", "MIDI Note No"]
            for i, text in enumerate(headers):
                label = ctk.CTkLabel(frame, text=text)
                label.grid(row=row_no, column=i, padx=5, pady=5)
            row_no += 1

            for hole_name, val2 in val["Holes"].items():
                # Hole No.
                hole_label = ctk.CTkLabel(frame, text=str(val2["hole_no"]))
                hole_label.grid(row=row_no, column=0, padx=5, pady=2)

                # Name
                name_entry = ctk.CTkLabel(frame, text=hole_name)
                name_entry.grid(row=row_no, column=1, padx=5, pady=2)

                # Note Number
                tmp = MyCTkIntInput(frame, width=50)
                tmp.insert(0, val2["midi_note_no"])
                tmp.grid(row=row_no, column=2, padx=5, pady=2)
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
