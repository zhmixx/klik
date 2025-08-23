import base64
import hashlib
import json
import sys
import random
import os
import uuid
from main import *

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

def klik():
    global kliks, klikmulti, exp, normal_colors, darkened_colors
    kliks += klikmulti
    klikfg = random.choice(normal_colors)
    klikhv = random.choice(darkened_colors)
    klikamount.configure(text=f"kliks: {kliks}")
    gain_exp(int(klikmulti * 2))

def open_shop():
    pg1.pack_forget()
    pg2.pack(fill="both", expand=True)

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


# kira will take care of that (i think) - zhmixx