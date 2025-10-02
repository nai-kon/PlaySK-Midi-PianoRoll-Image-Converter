from config import ConfigMng
from converter_base import BaseConverter
from PIL import Image, ImageDraw


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
        self.custom_note_map = {
            # channel_no: {original_note_number: new_note_number, ...}, ...
            0: {note_no: note_no * 2 - 24 for note_no in range(127)},  # lower keyboard
            1: {note_no: note_no * 2 - 25 for note_no in range(127)},  # upper keyboard
            14: {note_no: 13 + note_no * 2 for note_no in range(0, 17)} | {note_no: 129 + note_no * 2 for note_no in range(17, 30)},  # lower control holes
            15: {note_no: 14 + note_no * 2 for note_no in range(0, 17)} | {note_no: 130 + note_no * 2 for note_no in range(17, 30)},  # upper control holes
        }
        self.hole_x_list = [self._get_hole_x(i) for i in range(512)]
        self.out_img: Image.Image | None = None
        self.draw: ImageDraw | None = None