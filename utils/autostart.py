import os
import sys
import subprocess
from pathlib import Path

TASK_NAME = "DeadInsideDaily"


def add_to_startup():
    """Добавляет приложение в автозапуск.

    Поддерживаем Windows (schtasks) и Linux (XDG autostart .desktop).
    """
    app_path = os.path.abspath(sys.argv[0])
    if sys.platform.startswith("win"):
        cmd = (
            f'schtasks /Create /SC ONLOGON /TN "{TASK_NAME}" '
            f'/TR "{app_path}" /F'
        )
        subprocess.run(cmd, shell=True)
        return

    # Linux: write .desktop file to ~/.config/autostart
    if sys.platform.startswith("linux"):
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        desktop_path = autostart_dir / f"{TASK_NAME}.desktop"
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=DeadInside
Exec={app_path}
X-GNOME-Autostart-enabled=true
"""
        desktop_path.write_text(desktop_entry)
        return

    # macOS and others: not implemented


def remove_from_startup():
    """Удаляет автозапуск для ОС."""
    if sys.platform.startswith("win"):
        cmd = f'schtasks /Delete /TN "{TASK_NAME}" /F'
        subprocess.run(cmd, shell=True)
        return

    if sys.platform.startswith("linux"):
        desktop_path = Path.home() / ".config" / "autostart" / f"{TASK_NAME}.desktop"
        try:
            desktop_path.unlink()
        except FileNotFoundError:
            pass
        return


def is_in_startup():
    """Проверяет, добавлено ли приложение в автозапуск на текущей платформе."""
    if sys.platform.startswith("win"):
        result = subprocess.run(
            f'schtasks /Query /TN "{TASK_NAME}"',
            shell=True, capture_output=True, text=True)
        return result.returncode == 0

    if sys.platform.startswith("linux"):
        desktop_path = Path.home() / ".config" / "autostart" / f"{TASK_NAME}.desktop"
        return desktop_path.exists()

    return False
