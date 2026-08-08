import customtkinter as ctk
from datetime import date
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import threading

from data.data_manager import (
    load_data,
    get_days_remaining,
    add_or_update_note_today,
    get_total_days,
    clear_goal
)
from ui.history_window import HistoryWindow


class DailyWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DeadInside")  # или DueIt — на твой вкус
        self.geometry("700x480")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")

        data = load_data()
        self.goal = data["goal"]
        self.deadline = date.fromisoformat(data["deadline"]) if data["deadline"] else None

        self.build_ui()

        # Настройка системного трея
        self.tray_icon = None
        self.tray_thread = None
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def build_ui(self):
        # Заголовок с целью
        self.goal_label = ctk.CTkLabel(
            self, text=f"🎯 {self.goal}", font=("Segoe UI", 18, "bold")
        )
        self.goal_label.pack(pady=(30, 10))

        # Прогресс-бар
        days_left = get_days_remaining()
        total_days = get_total_days() or 1
        progress = max(0.0, min(1.0, (total_days - days_left) / total_days))

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(progress)
        self.progress.pack(pady=10)

        self.days_text = (
            f"Осталось дней: {days_left}" if days_left > 0 else "🔥 Дедлайн сегодня! 🎉"
        )
        self.days_label = ctk.CTkLabel(
            self, text=self.days_text, font=("Segoe UI", 24, "bold")
        )
        self.days_label.pack(pady=5)

        # Поле для заметки
        self.note_label = ctk.CTkLabel(
            self, text="Что ты сделал сегодня для цели? 📝", font=("Segoe UI", 14)
        )
        self.note_label.pack(pady=(20, 5))

        self.note_text = ctk.CTkTextbox(
            self,
            width=550,
            height=120,
            font=("Segoe UI", 13),
            border_width=1,
            border_color="#bdc3c7",
            corner_radius=8,
        )
        self.note_text.pack(pady=10)

        # Загружаем заметку за сегодня, если есть
        data = load_data()
        today_str = date.today().isoformat()
        note_today = ""
        for n in data["notes"]:
            if n["date"] == today_str:
                note_today = n["text"]
                break
        self.note_text.insert("0.0", note_today)

        # Панель кнопок
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Сохранить ✅",
            command=self.save_note,
            width=140,
            height=40,
            fg_color="#2e7d32",
        )
        self.save_btn.grid(row=0, column=0, padx=10)

        self.history_btn = ctk.CTkButton(
            btn_frame,
            text="📋 История",
            command=self.open_history,
            width=140,
            height=40,
            fg_color="#1976d2",
        )
        self.history_btn.grid(row=0, column=1, padx=10)

        self.close_btn = ctk.CTkButton(
            btn_frame,
            text="Свернуть в трей",
            command=self.hide_to_tray,
            width=140,
            height=40,
            fg_color="#757575",
        )
        self.close_btn.grid(row=0, column=2, padx=10)

        self.manage_btn = ctk.CTkButton(
            btn_frame,
            text="⚙️ Управление",
            command=self.manage_goal,
            width=140,
            height=40,
            fg_color="#f57c00",
            hover_color="#e65100",
        )
        self.manage_btn.grid(row=0, column=3, padx=10)

    def save_note(self):
        note = self.note_text.get("0.0", "end").strip()
        if note:
            add_or_update_note_today(note)
            self.save_btn.configure(text="✅ Сохранено!", fg_color="#388e3c")
            self.after(1500, lambda: self.save_btn.configure(text="Сохранить ✅", fg_color="#2e7d32"))
        else:
            messagebox.showinfo("Пусто", "Заметка пуста, сохранение не выполнено.")

    def open_history(self):
        HistoryWindow(self)

    def hide_to_tray(self):
        """Сворачивает окно в трей, не закрывая приложение."""
        self.withdraw()
        if self.tray_icon is None:
            self.create_tray_icon()

    def create_tray_icon(self):
        """Создаёт иконку в системном трее."""
        # Генерация простой иконки 64x64
        image = Image.new("RGB", (64, 64), color="white")
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, 60, 60], fill="#2e7d32", outline="#1b5e20", width=3)
        draw.text((24, 18), "D", fill="white", size=30)  # Можешь заменить на свою букву/лого

        menu = pystray.Menu(
            pystray.MenuItem("Открыть", self.show_window),
            pystray.MenuItem("Выход", self.quit_app),
        )

        self.tray_icon = pystray.Icon("DeadInside", image, "DeadInside – твой шаг к цели", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def show_window(self, icon=None, item=None):
        """Восстанавливает окно из трея."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self, icon=None, item=None):
        """Полностью завершает работу приложения."""
        if self.tray_icon is not None:
            self.tray_icon.stop()
        self.destroy()

    def manage_goal(self):
        """Открывает окно управления текущей целью."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Управление целью")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Текущая цель:", font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text=self.goal, wraplength=350).pack(pady=5)

        reset_btn = ctk.CTkButton(
            dialog,
            text="🗑️ Сбросить цель и начать заново",
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=lambda: self.confirm_reset(dialog),
        )
        reset_btn.pack(pady=15)

        # Здесь можно добавить дополнительные кнопки (например, архив заметок)

    def confirm_reset(self, dialog):
        """Подтверждение сброса цели и всех данных."""
        if messagebox.askyesno(
            "Подтверждение",
            "Удалить текущую цель и все заметки безвозвратно?",
        ):
            clear_goal()           # удаляет JSON-файл с данными
            dialog.destroy()
            self.quit_app()        # закрывает окно и трей
            # Перезапуск приложения, чтобы открылось окно настройки
            import main
            main.restart_app()