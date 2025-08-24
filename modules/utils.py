import base64
import hashlib
import json
import sys
import random
import os
import uuid
from cryptography.fernet import Fernet
import modules.config as c

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

def derive_key(user_id: str) -> bytes:
    hash_bytes = hashlib.sha256(user_id.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

def save_variables(variables: dict, filename: str = "data.klik"):
    json_data = json.dumps(variables, indent=4).encode()
    fernet = Fernet(derive_key(c.USER_ID))
    encrypted_data = fernet.encrypt(json_data)
    with open(get_appdata_file(filename), "wb") as f:
        f.write(encrypted_data)

def load_variables(filename: str = "data.klik") -> dict:
    fernet = Fernet(derive_key(c.USER_ID))
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
    exp += amount
    c.expamount.configure(text=f"exp: {exp}/{exp_to_next}")
    while exp >= exp_to_next:
        exp -= exp_to_next
        c.level += 1
        exp_to_next = int(100 * (c.level**1.5))
        c.level_label.configure(text=f"level: {c.level}")
        index = random.randint(0, len(c.normal_colors) - 1)
        c.kliker.configure(
            fg_color=c.normal_colors[index], hover_color=c.darkened_colors[index]
        )
    c.expamount.configure(text=f"exp: {exp}/{exp_to_next}")
    c.levelbar.set(exp / exp_to_next)

def klik():
    c.kliks += c.klikmulti
    c.klikamount.configure(text=f"kliks: {c.kliks}")
    gain_exp(int(c.klikmulti * 2))

def open_shop():
    c.pg1.pack_forget()
    c.pg2.pack(fill="both", expand=True)

def get_savevars():
    return {
        "kliks": c.kliks,
        "level": c.level,
        "exp": c.exp,
        "exp_to_next": c.exp_to_next,
        "klikmulti": c.klikmulti,
        "items_multi": c.items_multi,
        "items": c.items,
    }

def autoclicker(speed: int):
    global autoclick_job
    if autoclick_job is not None:
        c.app.after_cancel(autoclick_job)

    def run():
        global autoclick_job
        klik()
        autoclick_job = c.app.after(int(4000 / speed), run)

    run()

def buy(item: str):
    if item in c.items:
        price = c.items[item]
        if kliks >= price:
            kliks -= price
            c.klikamount.configure(text=f"kliks: {kliks}")
            exp += int(price * 0.5)
            c.expamount.configure(text=f"exp: {exp}")
            c.items[item] = int(c.items[item] * 1.3)
            c.items_multi[item] += 1
            if item == "click_upgrade":
                klikmulti = int(klikmulti * c.items_multi["click_upgrade"])
            elif item == "autoclicker":
                autoclicker(c.items_multi["autoclicker"])
            c.statuslabel.configure(text=f"successfully bought {item}")
            c.buy_clicks.configure(text=f"upgrade klik: {c.items['click_upgrade']}")
            c.buy_autoclicker.configure(text=f"upgrade autokliker: {c.items['autoclicker']}")
        else:
            c.statuslabel.configure(text="not enough kliks!")
    else:
        print(f"ERROR: ITEM '{item}' DOES NOT EXIST")


# kira will take care of that (i think) - zhmixx