import json
import os
from datetime import date
import uuid

DATA_DIR = os.path.join(os.getenv('APPDATA'), 'DeadInside')
DATA_FILE = os.path.join(DATA_DIR, 'goal_data.json')
MAX_GOALS = 5

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """Загружает данные. Мигрирует старый одиночный формат в новый массив целей."""
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"goals": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Миграция старой структуры
    if "goal" in data and "deadline" in data:
        migrated_goal = {
            "id": str(uuid.uuid4()),
            "goal": data["goal"],
            "deadline": data["deadline"],
            "created": data.get("created", date.today().isoformat()),
            "notes": data.get("notes", [])
        }
        data = {"goals": [migrated_goal]}
        save_data(data)
    return data

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_goals():
    """Возвращает список целей."""
    return load_data()["goals"]

def can_add_goal():
    """Проверяет, не достигнут ли лимит целей."""
    return len(get_goals()) < MAX_GOALS

def add_goal(goal_text, deadline_date: date):
    """Добавляет новую цель. Возвращает True при успехе, иначе False."""
    if not can_add_goal():
        return False
    data = load_data()
    new_goal = {
        "id": str(uuid.uuid4()),
        "goal": goal_text,
        "deadline": deadline_date.isoformat(),
        "created": date.today().isoformat(),
        "notes": []
    }
    data["goals"].append(new_goal)
    save_data(data)
    return True

def delete_goal(goal_id):
    """Удаляет цель по ID."""
    data = load_data()
    data["goals"] = [g for g in data["goals"] if g["id"] != goal_id]
    save_data(data)

def get_goal(goal_id):
    """Возвращает данные цели по ID или None."""
    for g in get_goals():
        if g["id"] == goal_id:
            return g
    return None

def add_or_update_note(goal_id, note_text):
    """Добавляет/обновляет заметку за сегодня для указанной цели."""
    data = load_data()
    today_str = date.today().isoformat()
    for goal in data["goals"]:
        if goal["id"] == goal_id:
            for note in goal["notes"]:
                if note["date"] == today_str:
                    note["text"] = note_text
                    save_data(data)
                    return
            goal["notes"].append({"date": today_str, "text": note_text})
            save_data(data)
            return

def get_today_note(goal_id):
    """Возвращает текст заметки за сегодня для цели (или '')."""
    goal = get_goal(goal_id)
    if not goal:
        return ""
    today_str = date.today().isoformat()
    for note in goal["notes"]:
        if note["date"] == today_str:
            return note["text"]
    return ""

def get_days_remaining(goal_id):
    """Осталось дней до дедлайна цели (целое >=0)."""
    goal = get_goal(goal_id)
    if not goal:
        return None
    deadline = date.fromisoformat(goal["deadline"])
    delta = deadline - date.today()
    return max(delta.days, 0)

def get_total_days(goal_id):
    """Общее количество дней от создания до дедлайна."""
    goal = get_goal(goal_id)
    if not goal:
        return None
    created = date.fromisoformat(goal["created"])
    deadline = date.fromisoformat(goal["deadline"])
    return (deadline - created).days + 1