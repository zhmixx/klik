import base64
import hashlib
import json
import os
import random
import sys

import customtkinter
from PIL import Image
from cryptography.fernet import Fernet

from modules.config import config
from modules.utils import get_appdata_file, get_user_id

config.USER_ID = get_user_id()


def derive_key(user_id: str) -> bytes:
    hash_bytes = hashlib.sha256(user_id.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)


def save_variables(variables: dict, filename: str = "data.klik"):
    json_data = json.dumps(variables, indent=4).encode()
    fernet = Fernet(derive_key(config.USER_ID))
    encrypted_data = fernet.encrypt(json_data)
    with open(get_appdata_file(filename), "wb") as f:
        f.write(encrypted_data)


# apparently this function has no usages?
def load_variables(filename: str = "data.klik") -> dict:
    fernet = Fernet(derive_key(config.USER_ID))
    with open(get_appdata_file(filename), "rb") as f:
        encrypted_data = f.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


app = customtkinter.CTk()
app.geometry("600x500")
app.title("klik!!")

app.iconbitmap(resource_path("res/app.ico"))

pg1 = customtkinter.CTkFrame(app)
pg1.pack(fill="both", expand=True)

stats_row = customtkinter.CTkFrame(pg1, fg_color="transparent")
stats_row.pack(pady=5)
stats_row2 = customtkinter.CTkFrame(pg1, fg_color="transparent")
stats_row2.pack(pady=0)

click_row = customtkinter.CTkFrame(pg1, fg_color="transparent")
click_row.pack(expand=True)

btn_row = customtkinter.CTkFrame(pg1, fg_color="transparent")
btn_row.pack(pady=5)

levelbar = customtkinter.CTkProgressBar(stats_row2, orientation="horizontal", height=5)
levelbar.pack(side="top", padx=10, pady=1)
levelbar.set(0)
level_label = customtkinter.CTkLabel(
    stats_row, text=f"level: {config.level}", width=40, height=28, fg_color="transparent"
)
level_label.pack(side="left", padx=10, pady=0)

expamount = customtkinter.CTkLabel(
    stats_row,
    text=f"exp: {config.exp}/{config.exp_to_next}",
    width=40,
    height=28,
    fg_color="transparent",
)
expamount.pack(side="left", padx=10, pady=0)


def gain_exp(amount: int):
    config.exp += amount
    expamount.configure(text=f"exp: {config.exp}/{config.exp_to_next}")
    while config.exp >= config.exp_to_next:
        config.exp -= config.exp_to_next
        config.level += 1
        config.exp_to_next = int(100 * (config.level**1.5))
        level_label.configure(text=f"level: {config.level}")
        index = random.randint(0, len(normal_colors) - 1)
        kliker.configure(
            fg_color=config.normal_colors[index], hover_color=config.darkened_colors[index]
        )
    expamount.configure(text=f"exp: {config.exp}/{config.exp_to_next}")
    levelbar.set(config.exp / config.exp_to_next)


def klik():
    config.kliks += config.klikmulti
    klikamount.configure(text=f"kliks: {config.kliks}")
    gain_exp(int(config.klikmulti * 2))


klikimg = customtkinter.CTkImage(
    light_image=Image.open(resource_path("res/klik.png")),
    dark_image=Image.open(resource_path("res/klik.png")),
    size=(120, 120),
)

kliker = customtkinter.CTkButton(
    click_row,
    text="",
    width=120,
    height=120,
    command=klik,
    image=klikimg,
    fg_color="white",
    hover_color="gray",
)
kliker.pack(expand=True)

klikamount = customtkinter.CTkLabel(
    click_row, text=f"kliks: {config.kliks}", width=40, height=28, fg_color="transparent"
)
klikamount.pack(side="top")


def open_shop():
    pg1.pack_forget()
    pg2.pack(fill="both", expand=True)


shopbutton = customtkinter.CTkButton(
    btn_row, text="shop", width=140, height=28, command=open_shop
)
shopbutton.pack(pady=5, padx=5)


def get_savevars():
    return {
        "kliks": config.kliks,
        "level": config.level,
        "exp": config.exp,
        "exp_to_next": config.exp_to_next,
        "klikmulti": config.klikmulti,
        "items_multi": config.items_multi,
        "items": config.items,
    }


savebutton = customtkinter.CTkButton(
    btn_row,
    text="save",
    width=140,
    height=28,
    command=lambda: save_variables(get_savevars()),
)
savebutton.pack(pady=5, padx=5)

pg2 = customtkinter.CTkFrame(app)


def close_shop():
    pg2.pack_forget()
    pg1.pack(fill="both", expand=True)


close_shop = customtkinter.CTkButton(
    pg2, text="<< close shop", width=100, height=28, command=close_shop
)
close_shop.place(x=10, y=10)


statuslabel = customtkinter.CTkLabel(
    pg2, text="", width=40, height=28, fg_color="transparent"
)
statuslabel.pack(expand=True, side="bottom", padx=10)


def autoclicker(speed: int):
    if config.autoclick_job is not None:
        app.after_cancel(config.autoclick_job)

    def run():
        klik()
        config.autoclick_job = app.after(int(4000 / speed), run)

    run()


def buy(item: str):
    if item in config.items:
        price = config.items[item]
        if config.kliks >= price:
            config.kliks -= price
            klikamount.configure(text=f"kliks: {config.kliks}")
            config.exp += int(price * 0.5)
            expamount.configure(text=f"exp: {config.exp}")
            config.items[item] = int(config.items[item] * 1.3)
            config.items_multi[item] += 1
            if item == "click_upgrade":
                config.klikmulti = int(config.klikmulti * config.items_multi["click_upgrade"])
            elif item == "autoclicker":
                autoclicker(config.items_multi["autoclicker"])
            statuslabel.configure(text=f"successfully bought {item}")
            buy_clicks.configure(text=f"upgrade klik: {config.items['click_upgrade']}")
            buy_autoclicker.configure(
                text=f"upgrade autokliker: {config.items['autoclicker']}"
            )
        else:
            statuslabel.configure(text="not enough kliks!")
    else:
        print(f"ERROR: ITEM '{item}' DOES NOT EXIST")


buy_clicks = customtkinter.CTkButton(
    pg2,
    text=f"upgrade klik: {config.items['click_upgrade']}",
    width=140,
    height=28,
    command=lambda: buy("click_upgrade"),
)
buy_clicks.pack(expand=True)

buy_autoclicker = customtkinter.CTkButton(
    pg2,
    text=f"buy autokliker: {config.items['autoclicker']}",
    width=140,
    height=28,
    command=lambda: buy("autoclicker"),
)
buy_autoclicker.pack(expand=True)

try:
    klikamount.configure(text=f"kliks: {config.kliks}")
    level_label.configure(text=f"level: {config.level}")
    expamount.configure(text=f"exp: {config.exp}/{config.exp_to_next}")
    levelbar.set(config.exp / config.exp_to_next)
    buy_clicks.configure(text=f"upgrade klik: {config.items['click_upgrade']}")
    if config.items_multi["autoclicker"] > 1:
        buy_autoclicker.configure(text=f"upgrade autokliker: {config.items['autoclicker']}")
        autoclicker(config.items_multi["autoclicker"])
    else:
        buy_autoclicker.configure(text=f"buy autokliker: {config.items['autoclicker']}")
except FileNotFoundError:
    pass


def on_close():
    save_variables(get_savevars())
    app.destroy()


app.protocol("WM_DELETE_WINDOW", on_close)

app.mainloop()
