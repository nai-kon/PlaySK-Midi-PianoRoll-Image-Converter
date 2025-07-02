import webbrowser

import customtkinter as ctk
from PIL import Image

from const import APP_TITLE, APP_VERSION, COPY_RIGHT, LINK_COLOR


class WelcomMessage():
    def __init__(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent, label_text="")
        self.frame.grid(row=0, column=1, sticky="nsew")

        # drag & drop text
        image = ctk.CTkImage(light_image=Image.open("assets/folder_open_256dp_000000_FILL0_wght400_GRAD0_opsz48.png"), 
                             dark_image=Image.open("assets/folder_open_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(40, 40))
        ctk.CTkLabel(self.frame, image=image, compound="left", padx=15, text="Open or Drag MIDI FILE here!", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=(80, 50))

        # donation link
        donate_msg = ctk.CTkLabel(self.frame, text="Please donate for continuous development of the software", font=ctk.CTkFont(size=15, weight="bold"), text_color=LINK_COLOR)
        donate_msg._label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://paypal.me/KatzSasaki"))
        donate_msg._label.bind("<Enter>", lambda e: donate_msg.configure(cursor="hand2"))
        donate_msg._label.bind("<Leave>", lambda e: donate_msg.configure(cursor="arrow"))
        donate_msg.pack(pady=10, anchor="n", side="top")
        
        # project link
        project_link = ctk.CTkLabel(self.frame, text=APP_TITLE, text_color=LINK_COLOR)
        project_link._label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/nai-kon/Midi-Image-Converter"))
        project_link._label.bind("<Enter>", lambda e: project_link.configure(cursor="hand2"))
        project_link._label.bind("<Leave>", lambda e: project_link.configure(cursor="arrow"))
        project_link.pack()
        ctk.CTkLabel(self.frame, text=f"Version {APP_VERSION}\n{COPY_RIGHT}").pack()

        image = ctk.CTkImage(light_image=Image.open("assets/tooltip_2_256dp_000000_FILL0_wght400_GRAD0_opsz48.png"), 
                             dark_image=Image.open("assets/tooltip_2_256dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.png"), size=(40, 40))
        ctk.CTkLabel(self.frame, image=image, compound="left", padx=15, text="Tips", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20, anchor="w")

        image = Image.open("assets/hole_param1.png")
        image = ctk.CTkImage(image, size=(image.size[0] // 2, image.size[1] // 2))
        ctk.CTkLabel(self.frame, text="", image=image).pack(padx=20, anchor="e", side="right")

        ctk.CTkLabel(self.frame, text="- Currently, Multi-track midi file is not supported.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- Currently, tempo change event during music is not supported.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- Currently, 88-Note tracker bar is available. Will support more tracker bars.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- The default roll acceleration is 0.2% per feet, based on Stanford Univ paper.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- Sustain/soft pedal control change events are mapped to Hole #4 and #98 of 100 holes.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- Shorten hole length adjusts the note length shorter. MIDI are often longer than the actual hole.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- Image is saved as .PNG for efficient file size.").pack(padx=20, pady=5, anchor="w")
        ctk.CTkLabel(self.frame, text="- The parameters on the sidebar refer to these position.").pack(padx=20, pady=5, anchor="w")

        image = Image.open("assets/hole_param2.png")
        image = ctk.CTkImage(image, size=(image.size[0] // 1.5, image.size[1] // 1.5))
        ctk.CTkLabel(self.frame, text="", image=image).pack(padx=20, pady=15)
