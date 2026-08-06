import customtkinter as ctk
from datetime import date
from data.data_manager import load_data, get_days_remaining, add_or_update_note_today, get_total_days
from ui.history_window import HistoryWindow

class DailyWindow(ctk.CTk):
    """
    Главное окно приложения для ежедневного отслеживания прогресса цели.

    Отображает установленную цель, прогресс-бар (процент выполнения), количество
    оставшихся дней до дедлайна и поле для ввода ежедневной заметки о проделанной
    работе. Позволяет сохранять заметку, просматривать историю всех заметок и
    закрывать приложение.

    Methods:
        __init__(): инициализирует интерфейс, загружает данные цели,
            вычисляет прогресс и восстанавливает сегодняшнюю заметку (если есть).
        save_note(): извлекает текст из поля ввода и сохраняет его через
            add_or_update_note_today() с визуальным подтверждением.
        open_history(): открывает дочернее окно HistoryWindow для просмотра
            всех сохранённых заметок.
        on_close(): обработчик закрытия окна (WM_DELETE_WINDOW). В текущей
            реализации просто закрывает окно; в будущем можно добавить
            проверку несохранённых изменений.

    Atributs:
        goal (str): текст цели, загруженный из данных.
        deadline (date | None): дата дедлайна или None.
        progress (CTkProgressBar): виджет прогресс-бара.
        days_label (CTkLabel): отображает оставшиеся дни или сообщение о дедлайне.
        note_text (CTkTextbox): текстовое поле для заметки.
        save_btn (CTkButton): кнопка сохранения, меняет цвет при успехе.
        history_btn (CTkButton): кнопка открытия истории.
        close_btn (CTkButton): кнопка закрытия окна.

    Примечания:
        - Окно имеет фиксированный размер (550x480) и не изменяется.
        - Прогресс вычисляется как отношение прошедших дней от даты создания
          к общему сроку (от создания до дедлайна). Если дедлайн прошёл,
          прогресс устанавливается в 1.0 (100%).
        - При загрузке текущая заметка автоматически подставляется в текстовое поле.
        - Кнопка сохранения показывает временное сообщение "Сохранено!".
    """

    def __init__(self):
        super().__init__()
        self.title("Мой шаг к цели")
        self.geometry("550x480")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        
        data = load_data()
        self.goal = data["goal"]
        self.deadline = date.fromisoformat(data["deadline"]) if data["deadline"] else None
        
        # Заголовок с целью
        self.goal_label = ctk.CTkLabel(self, text=f"🎯 {self.goal}", font=("Segoe UI", 18, "bold"))
        self.goal_label.pack(pady=(30,10))
        
        # Прогресс-бар и дни
        days_left = get_days_remaining()
        total_days = get_total_days() or 1
        progress = max(0.0, min(1.0, (total_days - days_left) / total_days))
        
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(progress)
        self.progress.pack(pady=10)
        
        self.days_text = f"Осталось дней: {days_left}" if days_left > 0 else "🔥 Дедлайн сегодня! 🎉"
        self.days_label = ctk.CTkLabel(self, text=self.days_text, font=("Segoe UI", 24, "bold"))
        self.days_label.pack(pady=5)
        
        # Поле для заметки
        self.note_label = ctk.CTkLabel(self, text="Что ты сделал сегодня для цели? 📝", font=("Segoe UI", 14))
        self.note_label.pack(pady=(20,5))
        
        self.note_text = ctk.CTkTextbox(self, width=450, height=120, font=("Segoe UI", 13),
                                         border_width=1, border_color="#bdc3c7", corner_radius=8)
        self.note_text.pack(pady=10)
        
        # Загружаем заметку за сегодня, если есть
        today_str = date.today().isoformat()
        note_today = ""
        for n in data["notes"]:
            if n["date"] == today_str:
                note_today = n["text"]
                break
        self.note_text.insert("0.0", note_today)
        
        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        self.save_btn = ctk.CTkButton(btn_frame, text="Сохранить ✅", command=self.save_note,
                                      width=140, height=40, fg_color="#2e7d32")
        self.save_btn.grid(row=0, column=0, padx=10)
        
        self.history_btn = ctk.CTkButton(btn_frame, text="📋 История", command=self.open_history,
                                         width=140, height=40, fg_color="#1976d2")
        self.history_btn.grid(row=0, column=1, padx=10)
        
        self.close_btn = ctk.CTkButton(btn_frame, text="Закрыть", command=self.destroy,
                                       width=140, height=40, fg_color="#757575")
        self.close_btn.grid(row=0, column=2, padx=10)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def save_note(self):
        note = self.note_text.get("0.0", "end").strip()
        if note:
            add_or_update_note_today(note)
            # Визуальное подтверждение
            self.save_btn.configure(text="✅ Сохранено!", fg_color="#388e3c")
            self.after(1500, lambda: self.save_btn.configure(text="Сохранить ✅", fg_color="#2e7d32"))
        else:
            ctk.CTkMessagebox(title="Пусто", message="Заметка пуста, сохранение не выполнено.")
            
    def open_history(self):
        HistoryWindow(self)
        
    def on_close(self):
        # Предложить сохранить перед закрытием, если есть несохранённый текст
        current_note = self.note_text.get("0.0", "end").strip()
        # Здесь можно добавить проверку, если текст изменился, но для простоты просто закроем
        self.destroy()