import customtkinter as ctk
from data.data_manager import get_goals, delete_goal, can_add_goal
from ui.setup_window import SetupWindow
from ui.goal_detail import GoalDetailView
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import threading

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DeadInside")
        self.geometry("600x500")
        self.resizable(True, True)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        
        # Два основных контейнера
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)
        
        self.detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        # detail_frame будет показан позже
        
        # Трей
        self.tray_icon = None
        self.tray_thread = None
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        
        self.refresh_goals_list()
    
    def refresh_goals_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        goals = get_goals()
        
        title = ctk.CTkLabel(self.list_frame, text="Мои цели", font=("Segoe UI", 20, "bold"))
        title.pack(pady=20)
        
        if not goals:
            empty = ctk.CTkLabel(self.list_frame, text="У вас пока нет целей. Добавьте первую!")
            empty.pack(pady=10)
        else:
            for g in goals:
                self.create_goal_card(g)
        
        # Кнопка новой цели
        add_btn = ctk.CTkButton(self.list_frame, text="＋ Новая цель", command=self.open_setup,
                               width=200, height=40, fg_color="#2e7d32", hover_color="#1b5e20")
        add_btn.pack(pady=10)
        
        # --- Чекбокс автозагрузки ---
        autostart_state = is_in_startup()
        self.autostart_var = ctk.BooleanVar(value=autostart_state)
        self.autostart_check = ctk.CTkCheckBox(
            self.list_frame, 
            text="Запускать при входе в Windows",
            variable=self.autostart_var,
            command=self.toggle_autostart
        )
        self.autostart_check.pack(pady=5)
        
        self.list_frame.pack(fill="both", expand=True)
        self.detail_frame.pack_forget
    
    def create_goal_card(self, goal):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1, border_color="#bdc3c7")
        card.pack(pady=8, padx=20, fill="x")
        
        # Инфо о цели
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        goal_label = ctk.CTkLabel(info_frame, text=goal["goal"], font=("Segoe UI", 14, "bold"))
        goal_label.pack(anchor="w")
        
        # Осталось дней
        from data.data_manager import get_days_remaining
        days_left = get_days_remaining(goal["id"])
        days_text = f"Осталось дней: {days_left}" if days_left is not None else ""
        if days_text:
            days_lbl = ctk.CTkLabel(info_frame, text=days_text, font=("Segoe UI", 11))
            days_lbl.pack(anchor="w")
        
        # Кнопки справа
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        open_btn = ctk.CTkButton(btn_frame, text="Открыть", width=70, height=30,
                                command=lambda gid=goal["id"]: self.open_goal(gid))
        open_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(btn_frame, text="✕", width=30, height=30, fg_color="#d32f2f",
                                  hover_color="#b71c1c", command=lambda gid=goal["id"]: self.confirm_delete(gid))
        delete_btn.pack(side="left")
    
    def open_setup(self):
        if not can_add_goal():
            messagebox.showinfo(
                "Слишком много целей",
                "Вы ставите слишком много целей! Лучше сосредоточьте силы и внимание на уже поставленных, чтобы быстрее их достичь."
            )
            return
        setup = SetupWindow(on_goal_added=self.refresh_goals_list)
        # setup открывается как Toplevel, не блокирует mainloop
    
    def open_goal(self, goal_id):
        # Скрываем список, показываем детали
        self.list_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True)
        # Очищаем detail_frame и вставляем GoalDetailView
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        detail_view = GoalDetailView(self.detail_frame, goal_id, on_back_callback=self.show_list)
        detail_view.pack(fill="both", expand=True)
    
    def show_list(self):
        # Возвращаемся к списку целей
        self.detail_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        # Обновляем список (на случай изменений)
        self.refresh_goals_list()
    
    def confirm_delete(self, goal_id):
        if messagebox.askyesno("Удалить цель", "Вы уверены, что хотите удалить эту цель и все её заметки?"):
            delete_goal(goal_id)
            self.refresh_goals_list()
    
    # ----- методы трея (аналогично daily_window) -----
    def hide_to_tray(self):
        self.withdraw()
        if self.tray_icon is None:
            self.create_tray_icon()
    
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, 60, 60], fill='#2e7d32', outline='#1b5e20', width=3)
        draw.text((24, 18), "D", fill='white', size=30)
        menu = pystray.Menu(
            pystray.MenuItem("Открыть", self.show_window),
            pystray.MenuItem("Выход", self.quit_app)
        )
        self.tray_icon = pystray.Icon("DeadInside", image, "DeadInside", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()
    
    def show_window(self, icon=None, item=None):
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()