import sys
import os
import customtkinter as ctk

# Попытка импорта pywin32 для проверки единственного экземпляра
try:
    import win32event
    import win32api
    import winerror
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

from data.data_manager import load_data
from ui.setup_window import SetupWindow
from ui.daily_window import DailyWindow

MUTEX_NAME = "Global\\DeadInsideAppMutex"


def main():
    # Проверка, не запущено ли уже приложение (если доступен pywin32)
    if HAS_PYWIN32:
        try:
            mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                # Приложение уже работает – завершаем новую копию
                print("DeadInside уже работает в трее.")
                sys.exit(0)
        except Exception:
            # В редких случаях ошибка создания мьютекса – игнорируем
            pass

    # Загружаем данные: если нет цели или дедлайна → окно настройки
    data = load_data()
    if not data.get("goal") or not data.get("deadline"):
        # Скрываем главное окно CustomTkinter, чтобы не мешало
        root = ctk.CTk()
        root.withdraw()
        setup = SetupWindow(on_goal_set=lambda: start_daily())
        setup.mainloop()
    else:
        start_daily()


def start_daily():
    """Запускает основное ежедневное окно."""
    app = DailyWindow()
    app.mainloop()


def restart_app():
    """
    Полностью перезапускает текущий процесс.
    Используется после сброса цели, чтобы корректно показать окно настройки.
    """
    python = sys.executable
    os.execl(python, python, *sys.argv)


if __name__ == "__main__":
    main()