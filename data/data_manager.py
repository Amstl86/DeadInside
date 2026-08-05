import json
import os
from datetime import date, datetime

DATA_DIR = os.path.join(os.getenv('APPDATA'), 'GoalTracker')
DATA_FILE = os.path.join(DATA_DIR, 'goal_data.json')

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"goal": "", "deadline": "", "notes": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def set_goal(goal_text, deadline_date: date):
    data = {
        "goal": goal_text,
        "deadline": deadline_date.isoformat(),
        "notes": []
    }
    save_data(data)

def add_or_update_note_today(note_text):
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
    data = load_data()
    if not data["deadline"]:
        return None
    deadline = date.fromisoformat(data["deadline"])
    delta = deadline - date.today()
    return max(delta.days, 0)  # 0, если дедлайн прошёл

def get_total_days():
    data = load_data()
    if not data["deadline"] or not data.get("created"):
        return None
    created = date.fromisoformat(data["created"])
    deadline = date.fromisoformat(data["deadline"])
    return (deadline - created).days + 1

def set_creation_date():
    data = load_data()
    if "created" not in data:
        data["created"] = date.today().isoformat()
        save_data(data)