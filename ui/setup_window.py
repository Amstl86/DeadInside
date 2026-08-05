import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
from data.data_manager import set_goal, set_creation_date

class SetupWindow(ctk.CTkToplevel):
    def __init__(self, on_goal_set_callback):
        super().__init__()
        self.on_goal_set = on_goal_set_callback
        self.title("Новая цель")
        self.geometry("500x400")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")  # Следовать системной теме
        ctk.set_default_color_theme("green")
        
        self.goal_label = ctk.CTkLabel(self, text="Что ты хочешь достичь? 🎯", font=("Segoe UI", 16, "bold"))
        self.goal_label.pack(pady=(30,10))
        
        self.goal_entry = ctk.CTkEntry(self, placeholder_text="Например: выучить испанский до B1", width=400, height=40)
        self.goal_entry.pack(pady=10)
        
        # Вариант 1: выбрать дату дедлайна из календаря
        self.date_frame = ctk.CTkFrame(self)
        self.date_frame.pack(pady=10)
        self.date_label = ctk.CTkLabel(self.date_frame, text="Дата дедлайна 📅")
        self.date_label.grid(row=0, column=0, padx=5)
        self.deadline_date = DateEntry(self.date_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.deadline_date.grid(row=0, column=1, padx=5)
        self.deadline_date.set_date(date.today() + timedelta(days=30))
        
        # Вариант 2 (альтернативный): указать количество дней
        self.days_label = ctk.CTkLabel(self, text="Или укажи количество дней:")
        self.days_label.pack()
        self.days_spin = ctk.CTkEntry(self, placeholder_text="30", width=60, justify="center")
        self.days_spin.pack(pady=5)
        self.days_spin.insert(0, "30")
        
        self.info_label = ctk.CTkLabel(self, text="Оставь поле даты пустым, если используешь количество дней.",
                                       font=("Segoe UI", 10), text_color="gray")
        self.info_label.pack()
        
        self.start_btn = ctk.CTkButton(self, text="Начать 🚀", command=self.set_goal_action, width=200, height=45,
                                       fg_color="#2e7d32", hover_color="#1b5e20")
        self.start_btn.pack(pady=20)
        
    def set_goal_action(self):
        goal = self.goal_entry.get().strip()
        if not goal:
            self.show_error("Введи цель!")
            return
        
        # Определяем дедлайн
        if self.deadline_date.get():
            # Если дата в календаре отличается от сегодня, используем её
            try:
                deadline = self.deadline_date.get_date()
            except:
                self.show_error("Неверный формат даты")
                return
        else:
            days = self.days_spin.get().strip()
            if not days.isdigit():
                self.show_error("Введи число дней корректно")
                return
            days = int(days)
            if days < 1:
                self.show_error("Число дней должно быть больше 0")
                return
            deadline = date.today() + timedelta(days=days)
        
        set_goal(goal, deadline)
        set_creation_date()  # запомним дату создания
        self.destroy()
        self.on_goal_set()  # запускаем основное окно
        
    def show_error(self, msg):
        ctk.CTkMessagebox(title="Ошибка", message=msg, icon="cancel")