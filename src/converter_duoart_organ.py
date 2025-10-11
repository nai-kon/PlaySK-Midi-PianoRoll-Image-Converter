import customtkinter as ctk
from PIL import Image, ImageDraw

from config import ConfigMng
from converter_base import BaseConverter
from custom_widgets import CustomScrollableFrame


class DuoArtOrgan(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        self.roll_dpi = conf.dpi
        self.roll_tempo = conf.tempo
        self.roll_accelerate_rate_ft = float(conf.accel_rate) / 100 if conf.compensate_accel else 0

        # roll_width = 15.25
        # in inches
        self.roll_start_pad = 2
        self.roll_end_pad = 2
        self.roll_margin = conf.roll_side_margin
        self.hole_width = conf.hole_width  # 0.053333 inch
        self.chain_hole_spacing = conf.chain_perf_spacing
        self.single_hole_max_len = conf.single_hole_max_len
        self.leftest_hole_center = conf.leftest_hole_center  # 0.346666 inch
        self.rightest_hole_center = conf.roll_width - conf.rightest_hole_center  # 0.346666 inch
        self.vertial_offset = 0.25  
        self.hole_num = 176
        self.roll_color = 120  # in grayscale

        # in pixels
        self.roll_start_pad_px = int(self.roll_dpi * self.roll_start_pad)
        self.roll_end_pad_px = int(self.roll_dpi * self.roll_end_pad)
        self.roll_margin_px = int(self.roll_dpi * self.roll_margin)
        self.roll_width_px = int(self.roll_dpi * conf.roll_width)
        self.hole_width_px = int(self.roll_dpi * self.hole_width)
        self.chain_perforation_spacing_px = int(self.roll_dpi * self.chain_hole_spacing)
        self.single_hole_max_len_px = int(self.roll_dpi * self.single_hole_max_len)
        self.vertial_offset_px = int(self.roll_dpi * self.vertial_offset)
        self.shorten_hole_px = conf.shorten_len

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


# class DuoArtOrganSetting:
#     def __init__(self, parent: ctk.CTk):
#         self.dialog = CustomScrollableFrame(parent, fg_color=("#CCCCCC", "#111111"))
#         self.dialog.grid(row=0, column=0, sticky="nsew")    

#         # self.midi_settings = {
#         #     # hole_no: [name, midi_ch, midi_note_no]
#         #     # upper rows
#         #     1: 
#         # }
        
    
#         # MIDI setting for upper row holes

#         ctk.CTkLabel(self.dialog, text="Upper row holes (Swell)").pack(padx=10, anchor="w")


class DuoArtOrganSetting:
    def __init__(self, parent: ctk.CTk):
        self.dialog = CustomScrollableFrame(parent, fg_color=("#CCCCCC", "#111111"))
        self.dialog.grid(row=0, column=0, sticky="nsew")    

        self.midi_settings = {
            #"Hole Number", "Name", "MIDI Channel", "MIDI Note Number", midi_ch_obj, midi_noteno_obj]
            "Lower playing notes (Great)":{
                32: ["Great Lowest Note", 0, 0, None, None],
                146: ["Great Highest Note", 0, 0, None, None],
            },
            "Lower control holes (Great)": {
                # lower holes
                0: ["Great Tremolo", 0, 0, None, None],
                2: ["Great Tonal", 0, 0, None, None],
                4: ["Great Harp", 0, 0, None, None],
                6: ["Great Extension", 0, 0, None, None],
                8: ["Pedal 2nd Octave", 0, 0, None, None],
                10: ["Pedal 3rd Octave", 0, 0, None, None],
                12: ["Great Shade#1", 0, 0, None, None],
                14: ["Great Shade#2", 0, 0, None, None],
                16: ["Great Shade#3", 0, 0, None, None],
                18: ["Great Shade#4", 0, 0, None, None],
                20: ["Great Shade#5", 0, 0, None, None],
                22: ["Great Shade#6", 0, 0, None, None],
                24: ["Pedal Bassoon 16'", 0, 0, None, None],
                26: ["Pedal String 16'", 0, 0, None, None],
                28: ["Pedal Flute F 16'", 0, 0, None, None],
                30: ["Pedal Flute P 16'", 0, 0, None, None],
                148: ["Great String PP", 0, 0, None, None],
                150: ["Great String P", 0, 0, None, None],
                152: ["Great String F", 0, 0, None, None],
                154: ["Great Flute P", 0, 0, None, None],
                156: ["Great Flute F", 0, 0, None, None],
                158: ["Great Flute 4'", 0, 0, None, None],
                160: ["Great Diapason F", 0, 0, None, None],
                162: ["Great Piccolo", 0, 0, None, None],
                164: ["Great Clarinet", 0, 0, None, None],
                166: ["Great Trumpet", 0, 0, None, None],
                168: ["Chimes Dampers Off", 0, 0, None, None],
                170: ["L.C.W", 0, 0, None, None],
                172: ["L.C.W.", 0, 0, None, None],
                174: ["Ventil Control", 0, 0, None, None],
            },
            "Upper playing notes (Swell)":{
                33: ["Swell Lowest Note", 0, 0, None, None],
                147: ["Swell Highest Note", 0, 0, None, None],
            },
            "Upper control holes (Swell)":{

                1: ["Swell Echo", 0, 0, None, None],
                3: ["Swell Chimes", 0, 0, None, None],
                5: ["Swell Tremolo", 0, 0, None, None],
                7: ["Swell Harp", 0, 0, None, None],
                9: ["Swell Trumpet", 0, 0, None, None],
                11: ["Swell Oboe", 0, 0, None, None],
                13: ["Swell Vox Humana", 0, 0, None, None],
                15: ["Swell Diapason MF", 0, 0, None, None],
                17: ["Swell Flute 16'", 0, 0, None, None],
                19: ["Swell Flute 4'", 0, 0, None, None],
                21: ["Swell Flute P", 0, 0, None, None],
                23: ["Swell String Vibrato F", 0, 0, None, None],
                25: ["Swell String F", 0, 0, None, None],
                27: ["Swell String MF", 0, 0, None, None],
                29: ["Swell String P", 0, 0, None, None],
                31: ["Swell String PP", 0, 0, None, None],
                149: ["Swell Shade#1", 0, 0, None, None],
                151: ["Swell Shade#2", 0, 0, None, None],
                153: ["Swell Shade#3", 0, 0, None, None],
                155: ["Swell Shade#4", 0, 0, None, None],
                157: ["Swell Shade#5", 0, 0, None, None],
                159: ["Swell Shade#6", 0, 0, None, None],
                161: ["Swell Extension", 0, 0, None, None],
                163: ["L.C.W.", 0, 0, None, None],
                165: ["L.C.W.", 0, 0, None, None],
                167: ["Swell Soft Chimes", 0, 0, None, None],
                169: ["Reroll", 0, 0, None, None],
                171: ["Ventil Control", 0, 0, None, None],
                173: ["Normal", 0, 0, None, None],
                175: ["Pedal to Upper Holes", 0, 0, None, None],
            },
        }

        row_no = 0
        col_no = 0
        for key, val in self.midi_settings.items():
            if key == "Upper playing notes (Swell)":
                row_no = 0
                col_no = 4

            # label
            font = ctk.CTkFont(size=20)
            section = ctk.CTkLabel(self.dialog, text=key, font=font)
            section.grid(row=row_no, column=col_no, columnspan=4, padx=5, pady=(20, 10))
            row_no += 1

            # header
            headers = ["Hole No", "Name", "MIDI CH", "MIDI Note No"]
            for i, text in enumerate(headers):
                label = ctk.CTkLabel(self.dialog, text=text)
                label.grid(row=row_no, column=col_no + i, padx=5, pady=5)
            row_no += 1

            for hole_no, (hole_name, midi_ch, midi_no, _, _) in val.items():    
                # Hole No.
                hole_label = ctk.CTkLabel(self.dialog, text=str(hole_no))
                hole_label.grid(row=row_no, column=col_no, padx=5, pady=2)

                # Name
                name_entry = ctk.CTkLabel(self.dialog, text=hole_name)
                name_entry.grid(row=row_no, column=col_no + 1, padx=5, pady=2)

                # MIDI Channel
                tmp = ctk.CTkComboBox(self.dialog, values=[str(i) for i in range(16)], width=80)
                tmp.set(str(midi_ch))
                tmp.grid(row=row_no, column=col_no + 2, padx=5, pady=2)
                self.midi_settings[key][hole_no][3] = tmp

                # Note Number
                tmp = ctk.CTkComboBox(self.dialog, values=[str(i) for i in range(128)], width=80)
                tmp.set(str(midi_no))
                tmp.grid(row=row_no, column=col_no + 3, padx=5, pady=2)
                self.midi_settings[key][hole_no][4] = tmp

                row_no += 1

        dark_mode_btn = ctk.CTkButton(self.dialog, text="commit", width=20, command=self.debug)
        dark_mode_btn.grid(row=row_no, column=0, padx=5, pady=5)

    def debug(self):
        # debug
        for row_pos, val in self.midi_settings.items():
            for hole_no, [hole_name, midi_ch, midi_no, midi_ch_obj, midi_noteno_obj] in val.items():
                print(hole_name, midi_ch_obj.get(), midi_noteno_obj.get())


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x600")

    app.grid_columnconfigure(0, weight=1)  #
    app.grid_rowconfigure(0, weight=1)


    DuoArtOrganSetting(app)


    app.mainloop()