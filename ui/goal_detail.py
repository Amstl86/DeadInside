import customtkinter as ctk
from datetime import date
from data.data_manager import (
    get_goal, get_days_remaining, get_total_days,
    add_or_update_note, get_today_note
)
from tkinter import messagebox

class GoalDetailView(ctk.CTkFrame):
    def __init__(self, master, goal_id, on_back_callback):
        super().__init__(master, fg_color="transparent")
        self.goal_id = goal_id
        self.on_back = on_back_callback
        goal = get_goal(goal_id)
        if not goal:
            self.on_back()
            return
        
        self.goal_text = goal["goal"]
        self.build_ui()
    
    def build_ui(self):
        # Верхняя панель с кнопкой "Назад"
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(10,0), padx=10)
        
        back_btn = ctk.CTkButton(top_bar, text="← Назад", width=80, height=30,
                                fg_color="#757575", hover_color="#616161",
                                command=self.on_back)
        back_btn.pack(side="left")
        
        # Заголовок цели
        goal_label = ctk.CTkLabel(self, text=f"🎯 {self.goal_text}", font=("Segoe UI", 18, "bold"))
        goal_label.pack(pady=(10,5))
        
        # Прогресс
        days_left = get_days_remaining(self.goal_id)
        total_days = get_total_days(self.goal_id) or 1
        progress = max(0.0, min(1.0, (total_days - days_left) / total_days))
        
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(progress)
        self.progress_bar.pack(pady=5)
        
        days_text = f"Осталось дней: {days_left}" if days_left > 0 else "🔥 Дедлайн сегодня! 🎉"
        self.days_label = ctk.CTkLabel(self, text=days_text, font=("Segoe UI", 24, "bold"))
        self.days_label.pack(pady=5)
        
        # Поле заметки
        note_label = ctk.CTkLabel(self, text="Что ты сделал сегодня? 📝", font=("Segoe UI", 14))
        note_label.pack(pady=(10,5))
        
        self.note_text = ctk.CTkTextbox(self, width=500, height=90, font=("Segoe UI", 13),
                                         border_width=1, border_color="#bdc3c7", corner_radius=8)
        self.note_text.pack(pady=5)
        # Загружаем сегодняшнюю заметку
        today_note = get_today_note(self.goal_id)
        self.note_text.insert("0.0", today_note)
        
        save_btn = ctk.CTkButton(self, text="Сохранить ✅", command=self.save_note,
                                width=140, fg_color="#2e7d32")
        save_btn.pack(pady=5)
        
        # Разделитель и история
        history_label = ctk.CTkLabel(self, text="📋 История заметок", font=("Segoe UI", 16, "bold"))
        history_label.pack(pady=(15,5))
        
        self.history_frame = ctk.CTkScrollableFrame(self, width=500, height=200)
        self.history_frame.pack(pady=5, fill="both", expand=True, padx=10)
        self.populate_history()
    
    def save_note(self):
        note = self.note_text.get("0.0", "end").strip()
        if note:
            add_or_update_note(self.goal_id, note)
            # Показываем краткое подтверждение (можно лейбл)
            # И обновляем историю
            self.populate_history()
            messagebox.showinfo("Сохранено", "Заметка сохранена!")
        else:
            messagebox.showinfo("Пусто", "Заметка пуста.")
    
    def populate_history(self):
        # Очищаем фрейм истории
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        goal = get_goal(self.goal_id)
        if not goal:
            return
        notes = goal.get("notes", [])
        if not notes:
            empty_label = ctk.CTkLabel(self.history_frame, text="Пока нет заметок.")
            empty_label.pack(pady=10)
            return
        
        # Показываем в обратном порядке (сначала новые)
        for entry in reversed(notes):
            card = ctk.CTkFrame(self.history_frame, corner_radius=6, border_width=1, border_color="#bdc3c7")
            card.pack(pady=5, padx=5, fill="x")
            
            date_lbl = ctk.CTkLabel(card, text=entry["date"], font=("Segoe UI", 11, "bold"))
            date_lbl.pack(anchor="w", padx=10, pady=(5,0))
            
            text_lbl = ctk.CTkLabel(card, text=entry["text"], justify="left", wraplength=450)
            text_lbl.pack(anchor="w", padx=10, pady=5)