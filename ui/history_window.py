import customtkinter as ctk
from data.data_manager import load_data, save_data
from datetime import date

class HistoryWindow(ctk.CTkToplevel):
    """
    Окно для просмотра и управления историей ежедневных заметок.

    Это дочернее модальное окно загружает все сохранённые заметки из JSON-файла
    и отображает их в виде карточек в обратном хронологическом порядке (сначала новые).
    Каждая карточка содержит дату, текст заметки и кнопку удаления.

    Methods:
        populate_notes(): очищает прокручиваемую область и заполняет её карточками
            заметок на основе загруженных данных. Если заметок нет, выводит
            сообщение-заглушку.

        create_note_card(note_date, text): создаёт визуальную карточку для одной
            заметки. Включает в себя хедер с датой и кнопкой удаления, а также
            блок с текстом заметки.

        delete_note(note_date): обрабатывает удаление заметки. Показывает
            диалоговое окно подтверждения (CTkMessagebox) и, при согласии,
            фильтрует данные, сохраняет обновлённый файл и перерисовывает интерфейс.

    Atributs:
        data (dict): данные цели, загруженные через data_manager.load_data(),
            содержащие список заметок в поле "notes".
        scroll_frame (CTkScrollableFrame): контейнер с вертикальной прокруткой
            для размещения всех карточек заметок.

    Примечания:
        - Удаление происходит по дате (поле "date" в JSON). Если две заметки
          имеют одинаковую дату (что исключено логикой приложения), будет удалена
          первая подходящая.
        - После удаления окно не закрывается, а обновляет содержимое
          (вызов populate_notes()).
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("История заметок")
        self.geometry("550x550")
        self.resizable(True, True)
        
        self.data = load_data()
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=450)
        self.scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.populate_notes()
        
    def populate_notes(self):
        # Очистить фрейм
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        notes = self.data["notes"]
        if not notes:
            empty_label = ctk.CTkLabel(self.scroll_frame, text="Пока нет заметок.", font=("Segoe UI", 14))
            empty_label.pack(pady=30)
            return
        
        # Отображаем в обратном хронологическом порядке
        for entry in reversed(notes):
            self.create_note_card(entry["date"], entry["text"])
    
    def create_note_card(self, note_date, text):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8, border_width=1, border_color="#bdc3c7")
        card.pack(pady=8, padx=10, fill="x")
        
        # Дата и кнопка удаления в одной строке
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5,0))
        
        date_label = ctk.CTkLabel(header_frame, text=note_date, font=("Segoe UI", 12, "bold"))
        date_label.pack(side="left")
        
        delete_btn = ctk.CTkButton(header_frame, text="✕", width=30, height=25, fg_color="#d32f2f",
                                   hover_color="#b71c1c", command=lambda d=note_date: self.delete_note(d))
        delete_btn.pack(side="right")
        
        # Текст заметки
        text_label = ctk.CTkLabel(card, text=text, wraplength=450, justify="left",
                                  font=("Segoe UI", 12))
        text_label.pack(pady=10, padx=15, anchor="w")
    
    def delete_note(self, note_date):
        confirm = ctk.CTkMessagebox(title="Удалить?", message="Удалить эту заметку?",
                                    icon="question", option_1="Да", option_2="Нет")
        if confirm.get() == "Да":
            self.data["notes"] = [n for n in self.data["notes"] if n["date"] != note_date]
            save_data(self.data)
            self.populate_notes()