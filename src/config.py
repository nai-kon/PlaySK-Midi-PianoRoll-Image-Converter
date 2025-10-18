import json

from const import BASE_CONFIG_PATH, CONVERTER_CONFIG_PATHS


class ConfigMng:
    def __init__(self) -> None:
        self.tracker_name = ""
        self.tracker_config: dict = {}

        try:
            with open(BASE_CONFIG_PATH, encoding="utf-8") as f:
                self.base_config = json.load(f)
            self.load_tracker_config(self.base_config["tracker"])
        except FileNotFoundError:
            self.base_config = {}

    def load_tracker_config(self, tracker_name: str) -> bool:
        self.tracker_name = ""
        try:
            path = CONVERTER_CONFIG_PATHS.get(tracker_name, "")
            with open(path, encoding="utf-8") as f:
                self.tracker_config = json.load(f)
            self.tracker_name = tracker_name
        except FileNotFoundError:
            self.tracker_config = {}
            return False
        return True

    def save_config(self) -> None:
        try:
            with open(BASE_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.base_config, f, ensure_ascii=False, indent=4)

            path = CONVERTER_CONFIG_PATHS.get(self.tracker_name, "")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.tracker_config, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    obj = ConfigMng()
    print(obj.__dict__)

    obj.save_config()

    obj = ConfigMng()
    print(obj.__dict__)
