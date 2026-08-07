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
        setup = SetupWindow(on_goal_set_callback=lambda: start_daily())
        setup.mainloop()
    else:
        start_daily()

def start_daily():
    app = DailyWindow()
    app.mainloop()

if __name__ == "__main__":
    main()

"""
Баг: При постановки цели и выборе количиства дней, если пользователь не выбрал дату в календаре, то дедлайн остается 30 дней от текущей даты, даже если пользователь указал другое количество дней. Это происходит из-за того, что в коде при сохранении цели приоритет отдается дате из календаря, а если она не установлена, используется значение по умолчанию (30 дней).
Решение: Нужно изменить логику сохранения цели, чтобы приоритет отдавался количеству дней, если пользователь не выбрал дату в календаре. Если пользователь указал количество дней, то дедлайн должен рассчитываться исходя из текущей даты плюс указанное количество дней.
"""