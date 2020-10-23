import ctypes
import os
from pathlib import Path
from PySide2.QtCore import QLockFile


def is_running_as_admin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def user_home():
    return os.path.expanduser("~")


def clash_gui_config():
    path = Path("{}/.config/clash-gui".format(Path.home()))
    if not path.exists():
        path.mkdir(parents=True)
    return str(path)


def acquire_lock() -> bool:
    lock_file = QLockFile("./multi_instance.lock".format(clash_gui_config()))
    return lock_file.tryLock(timeout=500)
