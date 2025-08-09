from config import ConfigMng
from converter_base import BaseConverter


class AmpicoA(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        super().__init__(conf)

        # note length of long shaped holes need to be shorten
        normal_hole_h = 0.0625 * self.roll_dpi  # px
        crescendo_hole_h = 0.34 * self.roll_dpi  # px
        half_offset_h = (crescendo_hole_h - normal_hole_h) / 2
        self.custom_hole_offsets = {
            16: {"top_offset": half_offset_h, "bottom_offset": -half_offset_h},  # bass crescendo
            111: {"top_offset": half_offset_h, "bottom_offset": -half_offset_h}, # soft pedal
            113: {"top_offset": half_offset_h, "bottom_offset": -half_offset_h}, # treble crescendo
        }
