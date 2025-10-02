import json
import os

from pydantic import BaseModel

from const import ASSETS_DIR

CONFIG_PATH = os.path.join(ASSETS_DIR, "config.json")

class ConfigMng(BaseModel):
    dark_mode: bool =  True
    input_dir: str = ""
    output_dir: str = ""
    tracker: str = "88-Note"
    tempo: int = 80
    dpi: int = 300
    roll_width: float = 11.25
    leftest_hole_center: float = 0.14
    rightest_hole_center: float = 0.14
    roll_side_margin: float = 0.25
    hole_width: float = 0.07
    single_hole_max_len: float = 0.4
    chain_perf_spacing: float = 0.035
    shorten_len: int = 10
    compensate_accel: bool = True
    accel_rate: float = 0.18
    update_notified_version: str = ""
    
    def __init__(self):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        super().__init__(**data)

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))

if __name__ == "__main__":
    obj = ConfigMng()
    print(obj.__dict__)

    obj.save_config()

    obj = ConfigMng()
    print(obj.__dict__)
