from fastapi.testclient import TestClient
import os
import sys
import json


def test_conflicts_ack_and_listing(tmp_path, monkeypatch):
    db_file = tmp_path / "test_core.db"
    monkeypatch.setenv("CORE_DB_PATH", str(db_file))

    # reload modules
    for m in ("core.db", "core.api", "core.models", "core.sync"):
        if m in sys.modules:
            del sys.modules[m]

    from core.api import app
    from core.db import init_db, SessionLocal
    from core.models import OperationLog
    import core.sync as syncmod

    init_db()
    client = TestClient(app)

    # create an existing 'conflict_seen' op for item1
    db = SessionLocal()
    try:
        op = OperationLog(user_id="u1", item_id="item1", op_type="conflict_seen", payload=json.dumps({}), created_at=None)
        db.add(op)
        db.commit()
    finally:
        db.close()

    # monkeypatch detect_conflicts to return two items
    monkeypatch.setattr(syncmod, "detect_conflicts", lambda user_id, sa=None: ["item1", "item2"])

    r = client.get("/api/v1/sync/conflicts", params={"user_id": "u1"})
    assert r.status_code == 200
    data = r.json()
    assert set(data["conflicts"]) == {"item1", "item2"}
    assert data["unresolved_conflicts"] == ["item2"]

    # acknowledge item2 via ack endpoint
    r2 = client.post("/api/v1/sync/ack", json={"user_id": "u1", "item_id": "item2", "note": "seen"})
    assert r2.status_code == 200

    r3 = client.get("/api/v1/sync/conflicts", params={"user_id": "u1"})
    assert r3.status_code == 200
    assert r3.json()["unresolved_conflicts"] == []
