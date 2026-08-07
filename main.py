import sys
import customtkinter as ctk
from data.data_manager import load_data
from ui.setup_window import SetupWindow
from ui.daily_window import DailyWindow

def main():
    data = load_data()
    if not data["goal"] or not data["deadline"]:
        # Запуск окна настройки
        root = ctk.CTk()
        root.withdraw()  # скрываем главное окно
        setup = SetupWindow(on_goal_set=lambda: start_daily())
        setup.mainloop()
    else:
        start_daily()

def start_daily():
    app = DailyWindow()
    app.mainloop()

if __name__ == "__main__":
    main()