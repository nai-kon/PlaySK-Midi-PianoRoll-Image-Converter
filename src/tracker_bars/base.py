import os
import time

import mido
from PIL import Image, ImageDraw

from config import ConfigMng
from const import CONVERTER_CONFIG_PATHS


class BaseConverter:
    """88-note class for MIDI to Image conversion."""
    def __init__(self, conf: ConfigMng) -> None:
        self.roll_dpi = conf.tracker_config["dpi"]
        self.roll_tempo = conf.tracker_config["tempo"]
        self.roll_accelerate_rate_ft = float(conf.tracker_config["accel_rate"]) / 100 if conf.tracker_config["compensate_accel"] else 0

        # in inches
        self.roll_start_pad = 2
        self.roll_end_pad = 2
        self.roll_margin = conf.tracker_config["roll_side_margin"]
        self.hole_width = conf.tracker_config["hole_width"]
        self.chain_hole_spacing = conf.tracker_config["chain_perf_spacing"]
        self.single_hole_max_len = conf.tracker_config["single_hole_max_len"]
        self.leftest_hole_center = conf.tracker_config["leftest_hole_center"]
        self.rightest_hole_center = conf.tracker_config["roll_width"] - conf.tracker_config["rightest_hole_center"]
        self.hole_num = 100
        self.roll_color = 120  # in grayscale

        self.custom_hole_offsets: dict[int, dict[str, float]] = {
            # 88-note is not used. For Duo-Art or Ampico etc... 
            # note_number: {"top hole offset": XX (inch), "bottom hole offset": XX (inch)} 
        }  

        # in pixels
        self.roll_start_pad_px = int(self.roll_dpi * self.roll_start_pad)
        self.roll_end_pad_px = int(self.roll_dpi * self.roll_end_pad)
        self.roll_margin_px = int(self.roll_dpi * self.roll_margin)
        self.roll_width_px = int(self.roll_dpi * conf.tracker_config["roll_width"])
        self.hole_width_px = int(self.roll_dpi * self.hole_width)
        self.chain_perforation_spacing_px = int(self.roll_dpi * self.chain_hole_spacing)
        self.single_hole_max_len_px = int(self.roll_dpi * self.single_hole_max_len)
        self.shorten_hole_px = conf.tracker_config["shorten_len"]

        self.control_change_map: dict[int, int] = {
            # control_change_number: midiNoteNo
            64: 18,
            67: 113,
        }

        self.custom_note_map: dict[int, dict[int, int]] = {
            # channel_no: {original_note_number: new_note_number, ...}, 
            # not used in 88-note
        }

        self.hole_x_list = [self._get_hole_x(i) for i in range(128)]
        self.out_img: Image.Image
        self.draw: ImageDraw.ImageDraw

    def get_roll_acceleration_rate(self, px: float) -> float:
        cur_feet = px / self.roll_dpi / 12.0
        return (1 + self.roll_accelerate_rate_ft) ** cur_feet

    def _get_hole_x(self, note_no: int) -> int:
        return int(self.roll_dpi * (self.roll_margin + self.leftest_hole_center + ((note_no) * (self.rightest_hole_center - self.leftest_hole_center) / (self.hole_num - 1)) - (self.hole_width / 2)))

    def get_tick_to_px(self, tick_len, tempo: int, bpm: float, ppq: int) -> float:
        return ((tick_len * self.roll_dpi * tempo * 1.2) / (bpm * ppq))

    def draw_hole(self, note_no: int, tempo: int, bpm: float, ppq: int, on_tick: int, off_tick: int) -> None:
        hole_h: float = self.get_tick_to_px(off_tick - on_tick, tempo, bpm, ppq)
        hole_x: int = self.hole_x_list[note_no - 15]
        hole_y1: float = self.get_tick_to_px(on_tick, tempo, bpm, ppq) + self.roll_start_pad_px
        hole_y2: float = hole_y1 + hole_h
        
        # custom hole offsets
        if (offset := self.custom_hole_offsets.get(note_no)) is not None:
            hole_y1 += offset["top_offset"]
            hole_y2 += offset["bottom_offset"]

        # default hole offsets
        hole_y1 += self.shorten_hole_px / 2
        hole_y2 += -self.shorten_hole_px / 2
        hole_h = hole_y2 - hole_y1
        if hole_h < self.hole_width_px:
            hole_y1 -= (self.hole_width_px - hole_h) // 2
            hole_y2 += (self.hole_width_px - hole_h) // 2

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

    def convert(self, midi_path: str) -> bool:
        try:
            mid = mido.MidiFile(midi_path)
            ppq = mid.ticks_per_beat
            bpm = 80.0

            note_on_ticks: list[int] = [0] * 512
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
                        if msg.type == "control_change" and msg.control in self.control_change_map:
                            mapped_note_no = self.control_change_map[msg.control]
                            if msg.value > 0:
                                note_on_ticks[mapped_note_no] = abs_tick
                            elif note_on_ticks[mapped_note_no] != -1:
                                self.draw_hole(mapped_note_no, self.roll_tempo, bpm, ppq, note_on_ticks[mapped_note_no], abs_tick)
                                note_on_ticks[mapped_note_no] = -1  # some midi has error, msg.value=0 multiple time. So, ignore it.

                        if msg.type == "note_on" and msg.velocity > 0:
                            note_no = self.custom_note_map.get(msg.channel, {}).get(msg.note, msg.note)
                            note_on_ticks[note_no] = abs_tick
                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            note_no = self.custom_note_map.get(msg.channel, {}).get(msg.note, msg.note)
                            self.draw_hole(note_no, self.roll_tempo, bpm, ppq, note_on_ticks[note_no], abs_tick)

        except Exception as e:
            print(e)
            return False

        return True
            
    def saveimg(self, savepath: str) -> None:
        if self.out_img is not None:
            self.out_img.save(savepath)


def create_converter(name: str, conf: ConfigMng) -> BaseConverter:
    """Simple factory method of converter class"""
    convert_name = tuple(CONVERTER_CONFIG_PATHS.keys())
    if name == convert_name[1]:
        from tracker_bars.ampico import AmpicoA
        return AmpicoA(conf)
    if name == convert_name[2]:
        from tracker_bars.ampico import AmpicoB
        return AmpicoB(conf)
    elif name == convert_name[3]:
        from tracker_bars.duoart_organ import DuoArtOrgan
        return DuoArtOrgan(conf)
    elif name == convert_name[0]:
        return BaseConverter(conf)
    else:
        raise ValueError(f"Unknown converter type: {name}")


if __name__ == "__main__":
    input_dir = "C:\\Users\\sasaki\\Downloads\\Ampico_All_erolls\\test\\"
    output_dir = "output/classic/"
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mid"):
            path = os.path.join(input_dir, filename)
            conf = ConfigMng()
            t1 = time.time()
            m2i = BaseConverter(conf)
            m2i.convert(path)
            save_path = os.path.join(output_dir, os.path.basename(filename).replace(".mid", f" tempo{m2i.roll_tempo}.png"))
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            m2i.saveimg(save_path)

            print(f"Saved image to {save_path}")
            print(time.time() - t1, "sec")
