from datetime import date, timedelta

import pytest

from data import data_manager


@pytest.fixture
def isolated_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    data_manager.DATA_DIR = str(tmp_path / "DeadInside")
    data_manager.DATA_FILE = str(tmp_path / "DeadInside" / "goal_data.json")
    data_manager.ensure_data_dir()
    yield


def test_add_goal_rejects_empty_text(isolated_appdata):
    assert data_manager.add_goal("   ", date.today() + timedelta(days=3)) is False


def test_add_goal_rejects_deadline_in_past_or_today(isolated_appdata):
    assert data_manager.add_goal("Сделать проект", date.today()) is False
    assert data_manager.add_goal("Сделать проект", date.today() - timedelta(days=1)) is False


def test_load_data_handles_invalid_json(isolated_appdata):
    data_manager.ensure_data_dir()
    with open(data_manager.DATA_FILE, "w", encoding="utf-8") as f:
        f.write("{not valid json")

    data = data_manager.load_data()

    assert data == {"goals": []}


def test_add_or_update_note_replaces_note_for_today(isolated_appdata):
    assert data_manager.add_goal("Сделать задачу", date.today() + timedelta(days=5)) is True

    goal_id = data_manager.get_goals()[0]["id"]

    data_manager.add_or_update_note(goal_id, "Заметка 1")
    data_manager.add_or_update_note(goal_id, "Заметка 2")

    assert data_manager.get_today_note(goal_id) == "Заметка 2"


def test_get_days_remaining_returns_zero_for_overdue_goal(isolated_appdata):
    assert data_manager.add_goal("Сделать задачу", date.today() + timedelta(days=2)) is True

    goal = data_manager.get_goals()[0]
    data = data_manager.load_data()
    data["goals"][0]["deadline"] = (date.today() - timedelta(days=1)).isoformat()
    data_manager.save_data(data)

    assert data_manager.get_days_remaining(goal["id"]) == 0
