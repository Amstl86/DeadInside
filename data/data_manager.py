import json
import os
from datetime import date, datetime

DATA_DIR = os.path.join(os.getenv('APPDATA'), 'DeadInside')
DATA_FILE = os.path.join(DATA_DIR, 'goal_data.json')


def ensure_data_dir():
    """Создаёт папку для данных, если её нет."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_data():
    """Загружает данные из JSON-файла. Если файла нет, возвращает пустой словарь."""
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"goal": "", "deadline": "", "notes": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    """Сохраняет данные в JSON-файл."""
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def set_goal(goal_text, deadline_date: date):
    """
    Устанавливает новую цель и дату дедлайна.
    Полностью перезаписывает данные (старые заметки удаляются).
    """
    data = {
        "goal": goal_text,
        "deadline": deadline_date.isoformat(),
        "notes": []
    }
    save_data(data)


def add_or_update_note_today(note_text):
    """
    Добавляет или обновляет заметку за сегодняшний день.
    Если заметка за сегодня уже существует, она перезаписывается.
    """
    data = load_data()
    today_str = date.today().isoformat()

    # Ищем существующую заметку за сегодня
    for entry in data["notes"]:
        if entry["date"] == today_str:
            entry["text"] = note_text
            save_data(data)
            return

    # Иначе добавляем новую
    data["notes"].append({"date": today_str, "text": note_text})
    save_data(data)


def get_days_remaining():
    """
    Возвращает количество дней до дедлайна (целое число >= 0).
    Если дедлайн уже прошёл, возвращает 0.
    Если дедлайн не задан, возвращает None.
    """
    data = load_data()
    if not data.get("deadline"):
        return None
    deadline = date.fromisoformat(data["deadline"])
    delta = deadline - date.today()
    return max(delta.days, 0)


def get_total_days():
    """
    Возвращает общее количество дней от даты создания до дедлайна.
    Нужно для расчёта прогресс-бара.
    Если данных нет, возвращает None.
    """
    data = load_data()
    if not data.get("deadline") or not data.get("created"):
        return None
    created = date.fromisoformat(data["created"])
    deadline = date.fromisoformat(data["deadline"])
    return (deadline - created).days + 1  # +1, чтобы включить сегодняшний день


def set_creation_date():
    """
    Записывает дату создания цели (сегодня), если она ещё не была записана.
    """
    data = load_data()
    if "created" not in data:
        data["created"] = date.today().isoformat()
        save_data(data)


def clear_goal():
    """
    Удаляет файл данных, полностью сбрасывая цель и все заметки.
    """
    ensure_data_dir()
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)