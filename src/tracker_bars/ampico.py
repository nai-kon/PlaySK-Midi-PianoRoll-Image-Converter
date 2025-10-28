from config import ConfigMng

from .base import BaseConverter


class AmpicoA(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        super().__init__(conf)
        self.control_change_map = {}  # not used

        # note length of long shaped holes need to be shorten
        normal_hole_h = 0.0625 * self.roll_dpi  # px
        type1_hole_h = 0.175 * self.roll_dpi  # px.  for fast crescendo, sustain pedal
        type2_hole_h = 0.34 * self.roll_dpi  # px.  for slow crescendo, soft pedal

        self.custom_hole_offsets = {
            16: {"top_offset": (type2_hole_h - normal_hole_h) / 2, "bottom_offset": -(type2_hole_h - normal_hole_h) / 2},  # bass slow crescendo
            18: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # sustain pedal
            20: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # bass fast crescendo
            109: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # treble fast crescendo
            111: {"top_offset": (type2_hole_h - normal_hole_h) / 2, "bottom_offset": -(type2_hole_h - normal_hole_h) / 2}, # soft pedal
            113: {"top_offset": (type2_hole_h - normal_hole_h) / 2, "bottom_offset": -(type2_hole_h - normal_hole_h) / 2}, # treble slow crescendo
        }

class AmpicoB(BaseConverter):
    def __init__(self, conf: ConfigMng) -> None:
        super().__init__(conf)
        self.control_change_map = {}  # not used

        # note length of long shaped holes need to be shorten
        normal_hole_h = 0.0625 * self.roll_dpi  # px
        type1_hole_h = 0.175 * self.roll_dpi  # px.  for fast crescendo, sustain pedal
        type2_hole_h = 0.34 * self.roll_dpi  # px.  for slow crescendo, soft pedal
        intensity_offset = (1 / 64) * self.roll_dpi  # px.  sometimes said to be 1/32, but the actual measurement is 1/64.

        self.custom_hole_offsets = {
            15: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # amplifier
            17: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # bass intensity 2
            18: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # sustain pedal
            19: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # bass intensity 4
            21: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # bass intensity 6
            22: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # bass intensity cancel
            107: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # treble intensity cancel
            108: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # treble intensity 6
            109: {"top_offset": (type1_hole_h - normal_hole_h) / 2, "bottom_offset": -(type1_hole_h - normal_hole_h) / 2},  # treble fast crescendo
            110: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # treble intensity 4
            111: {"top_offset": (type2_hole_h - normal_hole_h) / 2, "bottom_offset": -(type2_hole_h - normal_hole_h) / 2}, # soft pedal
            112: {"top_offset": intensity_offset, "bottom_offset": intensity_offset},  # treble intensity 2
            113: {"top_offset": (type2_hole_h - normal_hole_h) / 2, "bottom_offset": -(type2_hole_h - normal_hole_h) / 2}, # treble slow crescendo
        }
