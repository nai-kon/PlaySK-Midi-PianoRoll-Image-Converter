import os

APP_TITLE = "PlaySK Midi to Piano Roll Image Converter"
APP_VERSION = "1.2.0"
COPY_RIGHT = "(C)Sasaki Katsumasa 2025"
LINK_COLOR = "#0066c0"
APP_WIDTH = 1200
APP_HEIGHT = 900
ASSETS_DIR = "playsk_midi_to_roll_image_converter_assets"
BASE_CONFIG_PATH = os.path.join(ASSETS_DIR, "config.json")
CONVERTER_CONFIG_PATHS = {
    "88-Note": os.path.join(ASSETS_DIR, "88-note config.json"),
    "Ampico A": os.path.join(ASSETS_DIR, "Ampico A config.json"),
    "Ampico B": os.path.join(ASSETS_DIR, "Ampico B config.json"),
    "Aeolian 176-note": os.path.join(ASSETS_DIR, "Aeolian 176-note config.json"),
}
