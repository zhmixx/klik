from dataclasses import dataclass
import json
import os
from cryptography.fernet import Fernet


def load_variables(filename: str = "data.klik") -> dict:
    fernet = Fernet(derive_key(config.USER_ID))

    appdata_path = os.getenv("APPDATA")
    if not appdata_path:
        raise RuntimeError("Unable to locate APPDATA directory")
    folder = os.path.join(appdata_path, "klik")
    os.makedirs(folder, exist_ok=True)
    fp = os.path.join(get_appdata_folder(), filename)

    with open(fp, "rb") as f:
        encrypted_data = f.read()
    decrypted_data = fernet.decrypt(encrypted_data)

    return json.loads(decrypted_data.decode())


@dataclass
class _Config:
    USER_ID: str = ""  # gets updated in main.py when app starts, changed to remove circular import
    kliks: int = 0
    level: int = 1
    exp: int = 0
    exp_to_next: int = 100
    klikmulti: int = 1

    items = {
        "click_upgrade": 50,
        "autoclicker": 100,
    }
    items_multi = {"click_upgrade": 1, "autoclicker": 1}

    app = None
    levelbar = None
    level_label = None
    expamount = None
    kliker = None
    klikamount = None
    statuslabel = None
    buy_clicks = None
    buy_autoclicker = None

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

    autoclick_job = None

    @classmethod
    def from_save(cls):
        return cls(**load_variables())


# still figuring out a way to make stuff work - zhmixx
config = _Config()
