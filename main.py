import customtkinter
from PIL import Image
import os
import uuid
from cryptography.fernet import Fernet
import base64
import hashlib
import json
import sys
import random

def get_appdata_folder() -> str:
    appdata_path = os.getenv('APPDATA')
    if not appdata_path:
        raise RuntimeError("we're fucked")
    folder = os.path.join(appdata_path, "klik")
    os.makedirs(folder, exist_ok=True)
    return folder

def get_appdata_file(filename: str) -> str:
    return os.path.join(get_appdata_folder(), filename)

def get_user_id() -> str:
    user_file = get_appdata_file("user.klik")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return f.read().strip()
    user_id = str(uuid.uuid4())
    with open(user_file, "w") as f:
        f.write(user_id)
    return user_id

USER_ID = get_user_id()

def derive_key(user_id: str) -> bytes:
    hash_bytes = hashlib.sha256(user_id.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

def save_variables(variables: dict, filename: str = "data.klik"):
    json_data = json.dumps(variables, indent=4).encode()
    fernet = Fernet(derive_key(USER_ID))
    encrypted_data = fernet.encrypt(json_data)
    with open(get_appdata_file(filename), "wb") as f:
        f.write(encrypted_data)

def load_variables(filename: str = "data.klik") -> dict:
    fernet = Fernet(derive_key(USER_ID))
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

kliks = 0
level = 1
exp = 0
exp_to_next = 100
klikmulti = 1

items = {
    "click_upgrade": 50,
    "autoclicker": 100,
}

items_multi = {"click_upgrade": 1, "autoclicker": 1}

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
    stats_row,
    text=f"level: {level}",
    width=40,
    height=28,
    fg_color="transparent"
)
level_label.pack(side="left", padx=10, pady=0)

expamount = customtkinter.CTkLabel(
    stats_row,
    text=f"exp: {exp}/{exp_to_next}",
    width=40,
    height=28,
    fg_color="transparent",
)
expamount.pack(side="left", padx=10, pady=0)

def gain_exp(amount: int):
    global exp, level, exp_to_next, levelbar
    exp += amount
    expamount.configure(text=f"exp: {exp}/{exp_to_next}")
    while exp >= exp_to_next:
        exp -= exp_to_next
        level += 1
        exp_to_next = int(100 * (level**1.5))
        level_label.configure(text=f"level: {level}")
        index = random.randint(0, len(normal_colors) - 1)
        kliker.configure(
            fg_color=normal_colors[index], hover_color=darkened_colors[index]
        )
    expamount.configure(text=f"exp: {exp}/{exp_to_next}")
    levelbar.set(exp / exp_to_next)

normal_colors = [
    "#FF0000",
    "#00FF00",
    "#0000FF",
    "#FFFF00",
    "#00FFFF",
    "#FF00FF",
    "#FFA500",
    "#800080",
]

darkened_colors = [
    "#800000",
    "#008000",
    "#000080",
    "#808000",
    "#008080",
    "#800080",
    "#804B00",
    "#400040",
]

def klik():
    global kliks, klikmulti, exp, normal_colors, darkened_colors
    kliks += klikmulti
    klikfg = random.choice(normal_colors)
    klikhv = random.choice(darkened_colors)
    klikamount.configure(text=f"kliks: {kliks}")
    gain_exp(int(klikmulti * 2))

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
    click_row, text=f"kliks: {kliks}", width=40, height=28, fg_color="transparent"
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
        "kliks": kliks,
        "level": level,
        "exp": exp,
        "exp_to_next": exp_to_next,
        "klikmulti": klikmulti,
        "items_multi": items_multi,
        "items": items,
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

autoclick_job = None

def autoclicker(speed: int):
    global autoclick_job
    if autoclick_job is not None:
        app.after_cancel(autoclick_job)

    def run():
        global autoclick_job
        klik()
        autoclick_job = app.after(int(4000 / speed), run)

    run()

def buy(item: str):
    global kliks, klikmulti, exp
    if item in items:
        price = items[item]
        if kliks >= price:
            kliks -= price
            klikamount.configure(text=f"kliks: {kliks}")
            exp += int(price * 0.5)
            expamount.configure(text=f"exp: {exp}")
            items[item] = int(items[item] * 1.3)
            items_multi[item] += 1
            if item == "click_upgrade":
                klikmulti = int(klikmulti * items_multi["click_upgrade"])
            elif item == "autoclicker":
                autoclicker(items_multi["autoclicker"])
            statuslabel.configure(text=f"successfully bought {item}")
            buy_clicks.configure(text=f"upgrade klik: {items['click_upgrade']}")
            buy_autoclicker.configure(text=f"upgrade autokliker: {items['autoclicker']}")
        else:
            statuslabel.configure(text="not enough kliks!")
    else:
        print(f"ERROR: ITEM '{item}' DOES NOT EXIST")


buy_clicks = customtkinter.CTkButton(
    pg2,
    text=f"upgrade klik: {items['click_upgrade']}",
    width=140,
    height=28,
    command=lambda: buy("click_upgrade"),
)
buy_clicks.pack(expand=True)

buy_autoclicker = customtkinter.CTkButton(
    pg2,
    text=f"buy autokliker: {items['autoclicker']}",
    width=140,
    height=28,
    command=lambda: buy("autoclicker"),
)
buy_autoclicker.pack(expand=True)

try:
    loaded = load_variables("data.klik")
    kliks = loaded.get("kliks", 0)
    level = loaded.get("level", 1)
    exp = loaded.get("exp", 0)
    exp_to_next = loaded.get("exp_to_next", 100)
    klikmulti = loaded.get("klikmulti", 1)
    items_multi = loaded.get("items_multi", {"click_upgrade": 1, "autoclicker": 1})
    items = loaded.get("items", {"click_upgrade": 50, "autoclicker": 100})

    klikamount.configure(text=f"kliks: {kliks}")
    level_label.configure(text=f"level: {level}")
    expamount.configure(text=f"exp: {exp}/{exp_to_next}")
    levelbar.set(exp / exp_to_next)
    buy_clicks.configure(text=f"upgrade klik: {items['click_upgrade']}")
    if items_multi["autoclicker"] > 1:
        buy_autoclicker.configure(text=f"upgrade autokliker: {items['autoclicker']}")
        autoclicker(items_multi["autoclicker"])
    else:
        buy_autoclicker.configure(text=f"buy autokliker: {items['autoclicker']}")
except FileNotFoundError:
    pass

def on_close():
    save_variables(get_savevars())
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_close)

app.mainloop()
