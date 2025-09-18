import json
import sys
import random
import os
from cryptography.fernet import Fernet
from modules.config import config as c


def get_appdata_folder() -> str:
    appdata_path = os.getenv("APPDATA")
    if not appdata_path:
        raise RuntimeError("Unable to locate APPDATA directory")
    folder = os.path.join(appdata_path, "klik")
    os.makedirs(folder, exist_ok=True)
    return folder


def get_appdata_file(filename: str) -> str:
    return os.path.join(get_appdata_folder(), filename)


def get_user_id() -> bytes:
    user_file = get_appdata_file("user.klik")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return eval(f.read().strip())
    user_id = Fernet.generate_key()
    with open(user_file, "w") as f:
        f.write(str(user_id))
    return user_id


def save_variables(variables: dict, filename: str = "data.klik"):
    json_data = json.dumps(variables, indent=4).encode()
    fernet = Fernet(c.USER_ID)
    encrypted_data = fernet.encrypt(json_data)
    with open(get_appdata_file(filename), "wb") as f:
        f.write(encrypted_data)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def gain_exp(amount: int):
    # this was working without saving to the actual config, not sure if intended - unseeyou
    c.exp += amount
    c.expamount.configure(text=f"exp: {c.exp}/{c.exp_to_next}")
    while c.exp >= c.exp_to_next:
        c.exp -= c.exp_to_next
        c.level += 1
        c.exp_to_next = int(100 * (c.level**1.5))
        c.level_label.configure(text=f"level: {c.level}")
        index = random.randint(0, len(c.normal_colors) - 1)
        c.kliker.configure(
            fg_color=c.normal_colors[index], hover_color=c.darkened_colors[index]
        )
    c.expamount.configure(text=f"exp: {c.exp}/{c.exp_to_next}")
    c.levelbar.set(c.exp / c.exp_to_next)


def klik():
    c.kliks += c.klikmulti
    c.klikamount.configure(text=f"kliks: {c.kliks}")
    gain_exp(int(c.klikmulti * 2))


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
    if c.autoclick_job is not None:
        c.app.after_cancel(c.autoclick_job)

    def run():
        klik()
        c.autoclick_job = c.app.after(int(4000 / speed), run)

    run()


def buy(item: str):
    if item in c.items:
        price = c.items[item]
        # same issue here - unseeyou
        if c.kliks >= price:
            c.kliks -= price
            c.klikamount.configure(text=f"kliks: {c.kliks}")
            c.exp += int(price * 0.5)
            c.expamount.configure(text=f"exp: {c.exp}")
            c.items[item] = int(c.items[item] * 1.3)
            c.items_multi[item] += 1
            if item == "click_upgrade":
                c.klikmulti = int(c.klikmulti * c.items_multi["click_upgrade"])
            elif item == "autoclicker":
                autoclicker(c.items_multi["autoclicker"])
            c.statuslabel.configure(text=f"successfully bought {item}")
            c.buy_clicks.configure(text=f"upgrade klik: {c.items['click_upgrade']}")
            c.buy_autoclicker.configure(
                text=f"upgrade autokliker: {c.items['autoclicker']}"
            )
        else:
            c.statuslabel.configure(text="not enough kliks!")
    else:
        print(f"ERROR: ITEM '{item}' DOES NOT EXIST")


# kira will take care of that (i think) - zhmixx
