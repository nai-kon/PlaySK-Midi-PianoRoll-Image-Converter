import os
import time

from mido import MidiFile
from PIL import Image, ImageDraw


class Midi2Image:
    def __init__(self):
        self.roll_dpi = 300
        self.roll_tempo = 95
        self.roll_width = int(11.25 * self.roll_dpi)
        self.roll_margin = 50
        self.hole_width = 18
        self.hole_y_margin = self.hole_width // 3
        self.hole_0_center = 36
        self.hole_99_center = 3340
        self.roll_color= 120  # grayscale
        self.reduce_px = 10
        self.chain_perforation_th_len = 85
        self.control_change_map = [
            {"controlChangeNo": 64, "midiNoteNo": 18},  # ControlChangeMap(64, 18)
			{"controlChangeNo": 67, "midiNoteNo": 113},	
		]
        self.hole_x_list = [self._get_hole_x(i) for i in range(128)]
        self.out_img = None
        self.draw = None

    def _get_hole_x(self, note_no):
        return int(self.roll_margin + self.hole_0_center + ((note_no) * (self.hole_99_center - self.hole_0_center) / 99) - (self.hole_width / 2))

    def get_tick_to_px(self, tick_len, tempo, bpm, ppq):
        return int((tick_len * self.roll_dpi * tempo * 1.2) / (bpm * ppq))

    def draw_hole(self, note_no, tempo, bpm, ppq, on_tick, off_tick):
        hole_h = self.get_tick_to_px(off_tick - on_tick, tempo, bpm, ppq) - self.reduce_px
        hole_h = max(hole_h, self.hole_width)
        hole_x = self.hole_x_list[note_no - 15]
        hole_y = self.out_img.height - self.get_tick_to_px(on_tick, tempo, bpm, ppq) - hole_h

		# Chain Perforation
        y = hole_y
        while y < hole_y + hole_h - self.chain_perforation_th_len:
            self.draw.ellipse([hole_x, y, hole_x + self.hole_width, y + self.hole_width], fill=255)
            y += self.hole_y_margin + self.hole_width

        # Normal perforation
        self.draw.rounded_rectangle([hole_x, y, hole_x + self.hole_width, hole_y + hole_h], radius=self.hole_width // 2, fill=255)

    def convert(self, midi_path, out_dir):
        mid = MidiFile(midi_path)
        ppq = mid.ticks_per_beat
        bpm = 80.0
        tempo = self.roll_tempo

        note_on_ticks = [0] * 128
        initialized = False

        for track in mid.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time

                if msg.type == "set_tempo" and not initialized:
                    tempo_micro = msg.tempo
                    bpm = 60_000_000.0 / tempo_micro
                    if tempo == 0:
                        tempo = int(round(bpm))
                    print(f"Tempo event at tick {abs_tick}: {bpm:.2f} BPM")

                    # 画像の初期化
                    width = self.roll_width + 2 * self.roll_margin
                    total_ticks = sum([t.time for t in track])
                    img_h = self.get_tick_to_px(total_ticks, tempo, bpm, ppq)
                    self.out_img = Image.new("L", (width, img_h), color=self.roll_color)
                    self.draw = ImageDraw.Draw(self.out_img)
                    self.draw.rectangle([0, 0, self.roll_margin, img_h], fill=255)
                    self.draw.rectangle([self.roll_margin + self.roll_width, 0, width, img_h], fill=255)
                    initialized = True

                if msg.type in ("note_on", "note_off", "control_change"):
                    note = msg.note if hasattr(msg, "note") else msg.control
                    velocity = msg.velocity if hasattr(msg, "velocity") else msg.value

                    for map in self.control_change_map:
                        if msg.type == "control_change" and note == map.controlChangeNo:
                            if velocity > 0:
                                note_on_ticks[map.midiNoteNo] = abs_tick
                            else:
                                self.draw_hole(map.midiNoteNo, tempo, bpm, ppq, note_on_ticks[map.midiNoteNo], abs_tick)

                    if msg.type == "note_on" and msg.velocity > 0:
                        note_on_ticks[note] = abs_tick
                    elif msg.type == "note_off" or  (msg.type == "note_on" and msg.velocity == 0):
                        self.draw_hole(note, tempo, bpm, ppq, note_on_ticks[note], abs_tick)

        if self.out_img:
            save_name = os.path.join(out_dir, os.path.basename(midi_path).replace(".mid", f" tempo{tempo}.png"))
            os.makedirs(os.path.dirname(save_name), exist_ok=True)
            self.out_img.save(save_name)
            print(f"Saved image to {save_name}")

if __name__ == "__main__":
    input_dir = "C:\\Users\\sasaki\\Downloads\\Ampico_All_erolls\\test\\"
    output_dir = "output/classic/"
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mid"):
            path = os.path.join(input_dir, filename)
            t1 = time.time()
            m2i = Midi2Image()
            m2i.convert(path, output_dir)
            print(time.time() - t1, "sec")