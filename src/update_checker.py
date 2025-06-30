import json
import platform
import re
import ssl
import threading
import time
import urllib
import urllib.request
import webbrowser

import certifi
import customtkinter as ctk
from PIL import Image

from config import ConfigMng
from const import APP_VERSION, LINK_COLOR


class UpdateMessage(ctk.CTkToplevel):
    def __init__(self, new_version: str):
        super().__init__()
        self.geometry("600x120")
        self.title("New Release")
        self.grab_set()

        image = ctk.CTkImage(light_image=Image.open("assets/campaign_256dp_000000_FILL0_wght400_GRAD0_opsz48.png"), 
                        dark_image=Image.open("assets/campaign_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(25, 25))
        ctk.CTkLabel(self, image=image, compound="left", padx=10, text=f"New Version {new_version} has been released!", font=ctk.CTkFont(size=20, weight="bold")).pack(expand=1)
        
        link = ctk.CTkLabel(self, text="https://github.com/nai-kon/Midi-Image-Converter/releases", font=ctk.CTkFont(size=15, weight="bold"), text_color=LINK_COLOR)
        link._label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/nai-kon/Midi-Image-Converter/releases"))
        link._label.bind("<Enter>", lambda e: link.configure(cursor="hand2"))
        link._label.bind("<Leave>", lambda e: link.configure(cursor="arrow"))
        link.pack(expand=1)


class NotifyUpdate:
    def __init__(self, conf: ConfigMng) -> None:
        self.conf = conf
        self.msg_show_delay = 3  # The main UI might be not launched yet, so wait for a while
        self.url = "https://playsk-roll-converter-update-checker.fxtch686.workers.dev/"

    def fetch_latest_version(self) -> str | None:
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
                "X-Identifier": "PlaySK",
                "X-Platform": platform.system(),
                "X-Version": APP_VERSION,
            })
            with urllib.request.urlopen(req, timeout=10, context=context) as res:
                title = json.loads(res.read().decode("utf8")).get("name", None)
                matched = re.findall(r"^Ver(\d.\d.\d)$", title)
                ver = matched[0] if matched else None

        except Exception:
            ver = None

        return ver

    def need_notify(self, ver: str | None) -> bool:
        print(ver, self.conf.update_notified_version, APP_VERSION)
        return (ver is not None and
            ver > self.conf.update_notified_version and
            ver > APP_VERSION)

    @classmethod
    def check(cls, conf: ConfigMng) -> threading.Thread:
        def check_func():
            obj = cls(conf)
            latest_ver = obj.fetch_latest_version()
            if obj.need_notify(latest_ver):
                time.sleep(obj.msg_show_delay)
                UpdateMessage(latest_ver)
                obj.conf.update_notified_version = latest_ver

        th = threading.Thread(target=check_func)
        th.start()
        return th
    
if __name__ == "__main__":
    import customtkinter as ctk

    app = ctk.CTk()
    conf = ConfigMng()
    NotifyUpdate.check(conf)
    conf.save_config()

    app.mainloop()