import datetime

from core.sync import _decide_merge, _parse_iso
from core.models import Item


def make_item(title: str, content: str, updated_at: datetime.datetime, version: int) -> Item:
    it = Item(title=title, content=content)
    it.updated_at = updated_at
    it.created_at = updated_at
    it.version = version
    return it


def test_apply_remote_when_local_missing():
    data = {"title": "R", "content": "remote", "updated_at": datetime.datetime.utcnow().isoformat(), "version": 1}
    apply_remote, conflict = _decide_merge(None, data)
    assert apply_remote is True
    assert conflict is False


def test_remote_higher_version_wins():
    now = datetime.datetime.utcnow()
    local = make_item("L", "local", now, 1)
    data = {"title": "R", "content": "remote", "updated_at": (now - datetime.timedelta(seconds=1)).isoformat(), "version": 2}
    apply_remote, conflict = _decide_merge(local, data)
    assert apply_remote is True
    assert conflict is False


def test_equal_version_close_timestamps_conflict():
    now = datetime.datetime.utcnow()
    local = make_item("L", "local", now, 2)
    # remote updated 2 seconds earlier, same version but different content
    data = {"title": "R", "content": "remote", "updated_at": (now - datetime.timedelta(seconds=2)).isoformat(), "version": 2}
    apply_remote, conflict = _decide_merge(local, data)
    assert apply_remote is False
    assert conflict is True
