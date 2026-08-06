"""
Модуль для управления данными трекера целей.
Хранит цель, дедлайн и ежедневные заметки в JSON-файле в папке пользователя.
"""

import json
import os
from datetime import date, datetime

DATA_DIR = os.path.join(os.getenv('APPDATA'), 'GoalTracker')
DATA_FILE = os.path.join(DATA_DIR, 'goal_data.json')

def ensure_data_dir():
    """
    Создаёт директорию для хранения данных, если она ещё не существует.
    Использует os.makedirs с параметром exist_ok=True, чтобы не вызывать ошибку,
    если папка уже есть.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """
    Загружает данные из JSON-файла.

    Если файла нет, возвращает словарь с пустыми полями:
        {"goal": "", "deadline": "", "notes": []}

    :return: dict: Словарь с ключами 'goal', 'deadline', 'notes'.
              В случае успешной загрузки — содержимое файла.
    """
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"goal": "", "deadline": "", "notes": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """
     Сохраняет словарь данных в JSON-файл с отступами для читаемости.

    Args:
        data (dict): Словарь, содержащий как минимум ключи 'goal', 'deadline', 'notes'.
                     Также может содержать 'created'.
    """
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def set_goal(goal_text, deadline_date: date):
    """
    Устанавливает новую цель и дедлайн, полностью перезаписывая старые данные.
    Список заметок сбрасывается (становится пустым).

    Args:
        goal_text (str): Текст цели.
        deadline_date (date): Объект datetime.date с датой дедлайна.
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

    Если заметка за сегодня уже существует, её текст заменяется на новый.
    Если нет — добавляется новая запись в конец списка.

    Args:
        note_text (str): Текст заметки.
    """
    data = load_data()
    today_str = date.today().isoformat()
    # Проверить, есть ли уже заметка за сегодня
    for entry in data["notes"]:
        if entry["date"] == today_str:
            entry["text"] = note_text
            save_data(data)
            return
    # Иначе добавить новую
    data["notes"].append({"date": today_str, "text": note_text})
    save_data(data)

def get_days_remaining():
    """
    Вычисляет количество дней, оставшихся до дедлайна.

    :return: int или None: Число оставшихся дней (неотрицательное). Если дедлайн не установлен,
             возвращает None. Если дедлайн уже прошёл, возвращает 0.
    """
    data = load_data()
    if not data["deadline"]:
        return None
    deadline = date.fromisoformat(data["deadline"])
    delta = deadline - date.today()
    return max(delta.days, 0)  # 0, если дедлайн прошёл

def get_total_days():
    """
    Вычисляет общее количество дней, отведённых на выполнение цели
    (от даты создания до дедлайна включительно).

    :return: int или None: Количество дней (дедлайн - создание + 1).
             Если дедлайн или дата создания не заданы, возвращает None.
    """
    data = load_data()
    if not data["deadline"] or not data.get("created"):
        return None
    created = date.fromisoformat(data["created"])
    deadline = date.fromisoformat(data["deadline"])
    return (deadline - created).days + 1

def set_creation_date():
    """
    Записывает дату создания цели, если она ещё не была установлена.

    Использует сегодняшнюю дату. Ничего не меняет, если ключ 'created' уже существует.
    Полезна для вызова сразу после установки цели, чтобы зафиксировать старт.
    """
    data = load_data()
    if "created" not in data:
        data["created"] = date.today().isoformat()
        save_data(data)