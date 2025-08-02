from config import ConfigMng
from converter_base import BaseConverter


class AmpicoA(BaseConverter):
    """Ampico A for MIDI to Image conversion."""    
    def __init__(self, conf: ConfigMng) -> None:
        super().__init__(conf)
        self.custom_hole_offsets = {
            16: {"top_offset": 41, "bottom_offset": -41},  # Duo-Art specific offsets
            111: {"top_offset": 41, "bottom_offset": -41}, # Ampico Soft Pedal
            113: {"top_offset": 41, "bottom_offset": -41}, # Ampico Treble Crescendo
        }
