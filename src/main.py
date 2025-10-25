import customtkinter
import tkinter as tk
import platform
from PIL import Image

from modules.config import config
from modules.utils import get_user_id, save_variables, resource_path, klik, buy, get_savevars, autoclicker

config.USER_ID = get_user_id()

app = customtkinter.CTk()
app.geometry("600x500")
app.title("klik!!")
config.app = app

if platform.system() == "Windows":
    app.iconbitmap(resource_path("res/app.ico"))
else:
    try:
        icon = tk.PhotoImage(file=resource_path("res/klik.png"))
        app.wm_iconphoto(True, icon)
    except Exception as e:
        print(f"failed to load window icon: {e}")

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
config.levelbar = levelbar
levelbar.pack(side="top", padx=10, pady=1)
levelbar.set(0)
level_label = customtkinter.CTkLabel(
    stats_row, text=f"level: {config.level}", width=40, height=28, fg_color="transparent"
)
level_label.pack(side="left", padx=10, pady=0)
config.level_label = level_label

expamount = customtkinter.CTkLabel(
    stats_row,
    text=f"exp: {config.exp}/{config.exp_to_next}",
    width=40,
    height=28,
    fg_color="transparent",
)
expamount.pack(side="left", padx=10, pady=0)
config.expamount = expamount

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

config.kliker = kliker

klikamount = customtkinter.CTkLabel(
    click_row, text=f"kliks: {config.kliks}", width=40, height=28, fg_color="transparent"
)
klikamount.pack(side="top")

config.klikamount = klikamount


def open_shop():
    pg1.pack_forget()
    pg2.pack(fill="both", expand=True)


shopbutton = customtkinter.CTkButton(
    btn_row, text="shop", width=140, height=28, command=open_shop
)
shopbutton.pack(pady=5, padx=5)

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
config.statuslabel = statuslabel

buy_clicks = customtkinter.CTkButton(
    pg2,
    text=f"upgrade klik: {config.items['click_upgrade']}",
    width=140,
    height=28,
    command=lambda: buy("click_upgrade"),
)
buy_clicks.pack(expand=True)
config.buy_clicks = buy_clicks

buy_autoclicker = customtkinter.CTkButton(
    pg2,
    text=f"buy autokliker: {config.items['autoclicker']}",
    width=140,
    height=28,
    command=lambda: buy("autoclicker"),
)
buy_autoclicker.pack(expand=True)
config.buy_autoclicker = buy_autoclicker

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
