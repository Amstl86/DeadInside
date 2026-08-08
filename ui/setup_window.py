import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
from data.data_manager import add_goal, can_add_goal
from tkinter import messagebox

class SetupWindow(ctk.CTkToplevel):
    def __init__(self, on_goal_added):
        super().__init__()
        self.on_goal_added = on_goal_added
        self.title("Новая цель")
        self.geometry("500x500")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        
        self.goal_label = ctk.CTkLabel(self, text="Что ты хочешь достичь? 🎯", font=("Segoe UI", 16, "bold"))
        self.goal_label.pack(pady=(30,10))
        
        self.goal_entry = ctk.CTkEntry(self, placeholder_text="Например: выучить испанский до B1", width=400, height=40)
        self.goal_entry.pack(pady=10)
        
        self.method_var = ctk.StringVar(value="days")
        
        self.radio_frame = ctk.CTkFrame(self)
        self.radio_frame.pack(pady=10)
        
        self.radio_days = ctk.CTkRadioButton(self.radio_frame, text="Указать количество дней", variable=self.method_var, value="days", command=self.toggle_method)
        self.radio_days.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.radio_calendar = ctk.CTkRadioButton(self.radio_frame, text="Выбрать дату в календаре", variable=self.method_var, value="calendar", command=self.toggle_method)
        self.radio_calendar.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.days_frame = ctk.CTkFrame(self)
        self.days_label = ctk.CTkLabel(self.days_frame, text="Количество дней до дедлайна:")
        self.days_label.pack(side="left", padx=5)
        self.days_entry = ctk.CTkEntry(self.days_frame, width=60, justify="center")
        self.days_entry.pack(side="left", padx=5)
        self.days_entry.insert(0, "30")
        self.days_frame.pack(pady=10, fill="x", padx=20)
        
        self.cal_frame = ctk.CTkFrame(self)
        self.cal_label = ctk.CTkLabel(self.cal_frame, text="Дата дедлайна 📅")
        self.cal_label.pack(side="left", padx=5)
        self.deadline_date = DateEntry(self.cal_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.deadline_date.pack(side="left", padx=5)
        self.deadline_date.set_date(date.today() + timedelta(days=30))
        # По умолчанию скрыт календарь
        self.cal_frame.pack_forget()
        
        self.start_btn = ctk.CTkButton(self, text="Начать 🚀", command=self.set_goal_action, width=200, height=45,
                                       fg_color="#2e7d32", hover_color="#1b5e20")
        self.start_btn.pack(pady=20)
        
    def toggle_method(self):
        if self.method_var.get() == "days":
            self.cal_frame.pack_forget()
            self.days_frame.pack(pady=10, fill="x", padx=20)
        else:
            self.days_frame.pack_forget()
            self.cal_frame.pack(pady=10, fill="x", padx=20)
        
    def set_goal_action(self):
        goal = self.goal_entry.get().strip()
        if not goal:
            messagebox.showerror("Ошибка", "Введи цель!")
            return
        
        if not can_add_goal():
            messagebox.showinfo(
                "Слишком много целей",
                "Вы ставите слишком много целей! Лучше сосредоточьте силы и внимание на уже поставленных, чтобы быстрее их достичь."
            )
            return
        
        if self.method_var.get() == "days":
            days_str = self.days_entry.get().strip()
            if not days_str.isdigit():
                messagebox.showerror("Ошибка", "Введи число дней корректно")
                return
            days = int(days_str)
            if days < 1:
                messagebox.showerror("Ошибка", "Число дней должно быть больше 0")
                return
            deadline = date.today() + timedelta(days=days)
        else:
            try:
                deadline = self.deadline_date.get_date()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            if deadline <= date.today():
                messagebox.showerror("Ошибка", "Дата дедлайна должна быть в будущем!")
                return
        
        success = add_goal(goal, deadline)
        if success:
            self.destroy()
            self.on_goal_added()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить цель. Возможно, превышен лимит.")