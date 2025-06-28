import customtkinter as ctk
from PIL import Image

Image.MAX_IMAGE_PIXELS = 10000000000

class RollViewer():
    def __init__(self, parent, width, height, image: Image.Image):
        self.view_width = width
        self.view_height = height
        
        scrollbar_w = 16

        # load image
        self.image = image
        self.img_w, self.img_h = self.image.size
        self.resize_ratio = self.view_width / self.img_w
        self.resize_img_h = int(self.img_h * self.resize_ratio)

        # スクロールバー（縦）
        self.offset_y = 0
        self.scrollbar = ctk.CTkScrollbar(parent, width=scrollbar_w, orientation="vertical", command=self.on_scrollbar)
        self.scrollbar.grid(row=0, column=2, sticky="ns")

        # initial crop
        cropped = self.image.crop((0, 0, self.img_w, int(self.view_height / self.resize_ratio)))
        cropped = cropped.resize((self.view_width, self.view_height))
        tk_image = ctk.CTkImage(light_image=cropped, size=(self.view_width, self.view_height))

        # 画像ラベル
        self.image_label = ctk.CTkLabel(parent, image=tk_image, text="")
        self.image_label.grid(row=0, column=1, sticky="nsew")

        # スクロールバーの初期値設定
        self.update_scrollbar()

        # リサイズイベント検出
        self.image_label.bind("<Configure>", self.on_resize)

        # マウスホイールでスクロール
        self.image_label.bind("<MouseWheel>", self.on_mousewheel)
   
    def on_resize(self, event):
        view_height = int(event.height / 2)  # 要DPI SCALE FACTOR
        if view_height != self.view_height:
            # ウィンドウの高さが変わったときに画像を更新
            self.view_height = view_height
            self.update_image()
            self.update_scrollbar()

    def update_image(self):
        offset_y_org = int(self.offset_y / self.resize_ratio)
        box = (0, offset_y_org, self.img_w, offset_y_org + int(self.view_height / self.resize_ratio))
        cropped = self.image.crop(box)
        cropped = cropped.resize((self.view_width, self.view_height))
        tk_image = ctk.CTkImage(light_image=cropped, size=(self.view_width, self.view_height))
        self.image_label.configure(image=tk_image)

    def clamp_offset(self):
        self.offset_y = max(0, min(self.offset_y, self.resize_img_h - self.view_height))

    def update_scrollbar(self):
        top = self.offset_y / self.resize_img_h
        bottom = (self.offset_y + self.view_height) / self.resize_img_h
        self.scrollbar.set(top, bottom)

    def on_mousewheel(self, event):
        self.offset_y -= event.delta
        self.clamp_offset()
        self.update_image()
        self.update_scrollbar()

    def on_scrollbar(self, *args):
        if args[0] == "moveto":
            self.offset_y = int(args[1] * self.resize_img_h)
        elif args[0] == "scroll":
            lines = int(args[1])
            self.offset_y += lines * 30
        
        self.clamp_offset()
        self.update_image()
        self.update_scrollbar()
