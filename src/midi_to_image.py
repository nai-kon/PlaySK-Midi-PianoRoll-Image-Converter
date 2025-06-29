import os
import time

import mido
from PIL import Image, ImageDraw


class Midi2Image:
    def __init__(
        self,
        roll_dpi: int = 300,
        roll_tempo: int = 95,
        roll_accelerate_rate_ft: float = 0.002,  # 0.2% per feet from Stanford Univ paper. set 0% without acceleration.
        roll_margin: float = 0.25,
        roll_width: float = 11.25,
        hole_width: float = 0.07,
        chain_hole_spacing: float = 0.035,
        single_hole_max_len: float = 0.4,
        hole_0_center: float = 0.14,  # from left edge of the roll
        hole_99_center: float = 0.14,  # from left edge of the roll
        shorten_hole_px: int = 10,
        roll_start_pad: float = 2,
        roll_end_pad: float = 2,
    ):
        self.roll_dpi = roll_dpi
        self.roll_tempo = roll_tempo
        self.roll_accelerate_rate_ft = roll_accelerate_rate_ft

        # in inches
        self.roll_start_pad = roll_start_pad
        self.roll_end_pad = roll_end_pad
        self.roll_margin = roll_margin
        self.roll_width = roll_width
        self.hole_width = hole_width
        self.chain_hole_spacing = chain_hole_spacing
        self.single_hole_max_len = single_hole_max_len
        self.hole_0_center = hole_0_center
        self.hole_99_center = roll_width - hole_99_center
        self.hole_num = 100
        self.roll_color = 120  # in grayscale

        # in pixels
        self.roll_start_pad_px = int(self.roll_dpi * self.roll_start_pad)
        self.roll_end_pad_px = int(self.roll_dpi * self.roll_end_pad)
        self.roll_margin_px = int(self.roll_dpi * self.roll_margin)
        self.roll_width_px = int(self.roll_dpi * self.roll_width)
        self.hole_width_px = int(self.roll_dpi * self.hole_width)
        self.chain_perforation_spacing_px = int(self.roll_dpi * self.chain_hole_spacing)
        self.single_hole_max_len_px = int(self.roll_dpi * self.single_hole_max_len)
        self.shorten_hole_px = shorten_hole_px

        self.control_change_map = [
            {"controlChangeNo": 64, "midiNoteNo": 18},
            {"controlChangeNo": 67, "midiNoteNo": 113},
        ]
        self.hole_x_list = [self._get_hole_x(i) for i in range(128)]
        self.out_img = None
        self.draw = None

    def get_roll_acceleration_rate(self, px: int) -> float:
        cur_feet = px / self.roll_dpi / 12.0
        return (1 + self.roll_accelerate_rate_ft) ** cur_feet

    def _get_hole_x(self, note_no):
        return int(self.roll_dpi * (self.roll_margin + self.hole_0_center + ((note_no) * (self.hole_99_center - self.hole_0_center) / (self.hole_num - 1)) - (self.hole_width / 2)))

    def get_tick_to_px(self, tick_len, tempo, bpm, ppq):
        return int(((tick_len * self.roll_dpi * tempo * 1.2) / (bpm * ppq)))

    def draw_hole(self, note_no, tempo, bpm, ppq, on_tick, off_tick):
        hole_h = self.get_tick_to_px(off_tick - on_tick, tempo, bpm, ppq) - self.shorten_hole_px
        hole_h = max(hole_h, self.hole_width_px)
        hole_x = self.hole_x_list[note_no - 15]
        hole_y1 = self.get_tick_to_px(on_tick, tempo, bpm, ppq) + self.roll_start_pad_px
        hole_y2 = hole_y1 + hole_h

        # compensate roll acceleration
        hole_y1 = int(hole_y1 * self.get_roll_acceleration_rate(hole_y1))
        hole_y2 = int(hole_y2 * self.get_roll_acceleration_rate(hole_y2))

        # convert coordinates
        hole_y1 = self.out_img.height - hole_y1
        hole_y2 = self.out_img.height - hole_y2

        # Chain Perforation
        y = hole_y2
        while y < hole_y1 - self.single_hole_max_len_px:
            self.draw.ellipse([hole_x, y, hole_x + self.hole_width_px, y + self.hole_width_px], fill=255)
            y += self.chain_perforation_spacing_px + self.hole_width_px

        # Normal perforation
        self.draw.rounded_rectangle([hole_x, y, hole_x + self.hole_width_px, hole_y1], radius=self.hole_width_px // 2, fill=255)

    def convert(self, midi_path) -> None:
        mid = mido.MidiFile(midi_path)
        ppq = mid.ticks_per_beat
        bpm = 80.0

        note_on_ticks = [0] * 128
        initialized = False
        total_ticks = 0
        for track in mid.tracks:
            total_ticks = max(sum([t.time for t in track]), total_ticks)

        for track in mid.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time

                if msg.type == "set_tempo" and not initialized:
                    bpm = 60_000_000.0 / msg.tempo
                    print(f"Tempo event at tick {abs_tick}: {bpm:.2f} BPM")

                    # create image
                    img_h = self.get_tick_to_px(total_ticks, self.roll_tempo, bpm, ppq) + self.roll_start_pad_px + self.roll_end_pad_px
                    print(bpm, ppq, total_ticks, img_h)
                    img_h = int(img_h * self.get_roll_acceleration_rate(img_h))
                    img_w = self.roll_width_px + 2 * self.roll_margin_px
                    self.out_img = Image.new("L", (img_w, img_h), color=self.roll_color)
                    self.draw = ImageDraw.Draw(self.out_img)
                    self.draw.rectangle([0, 0, self.roll_margin_px, img_h], fill=255)
                    self.draw.rectangle([self.roll_margin_px + self.roll_width_px, 0, img_w, img_h], fill=255)
                    initialized = True

                if msg.type in ("note_on", "note_off", "control_change"):
                    for map in self.control_change_map:
                        if msg.type == "control_change" and msg.control == map["controlChangeNo"]:
                            if msg.value > 0:
                                note_on_ticks[map["midiNoteNo"]] = abs_tick
                            else:
                                self.draw_hole(map["midiNoteNo"], self.roll_tempo, bpm, ppq, note_on_ticks[map["midiNoteNo"]], abs_tick)

                    if msg.type == "note_on" and msg.velocity > 0:
                        note_on_ticks[msg.note] = abs_tick
                    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                        self.draw_hole(msg.note, self.roll_tempo, bpm, ppq, note_on_ticks[msg.note], abs_tick)

    def saveimg(self, savepath: str) -> None:
        self.out_img.save(savepath)


if __name__ == "__main__":
    input_dir = "C:\\Users\\sasaki\\Downloads\\Ampico_All_erolls\\test\\"
    output_dir = "output/classic/"
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mid"):
            path = os.path.join(input_dir, filename)
            t1 = time.time()
            m2i = Midi2Image()
            m2i.convert(path)
            save_path = os.path.join(output_dir, os.path.basename(filename).replace(".mid", f" tempo{m2i.roll_tempo}.png"))
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            m2i.saveimg(save_path)

            print(f"Saved image to {save_path}")
            print(time.time() - t1, "sec")
