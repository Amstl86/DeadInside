from fastapi.testclient import TestClient
import os
import sys


def test_api_crud(tmp_path, monkeypatch):
    db_file = tmp_path / "test_core.db"
    monkeypatch.setenv("CORE_DB_PATH", str(db_file))

    # reload modules
    for m in ("core.db", "core.api", "core.models"):
        if m in sys.modules:
            del sys.modules[m]

    from core.api import app
    from core.db import init_db

    init_db()
    client = TestClient(app)

    r = client.post("/api/v1/items", json={"title": "t1", "content": "c1"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "t1"

    r2 = client.get("/api/v1/items")
    assert r2.status_code == 200
    items = r2.json()
    assert any(it["title"] == "t1" for it in items)


def test_auth_dev_fallback(tmp_path, monkeypatch):
    db_file = tmp_path / "test_core.db"
    monkeypatch.setenv("CORE_DB_PATH", str(db_file))
    monkeypatch.setenv("AUTH_MODE", "dev")

    for m in ("core.db", "core.api", "core.models"):
        if m in sys.modules:
            del sys.modules[m]

    from core.api import app
    from core.db import init_db

    init_db()
    client = TestClient(app)

    r = client.post("/api/v1/verify_token", json={"id_token": "dev-token"})
    assert r.status_code == 200, r.text
    assert r.json()["uid"] == "dev-user"

    r2 = client.post("/api/v1/refresh_token", json={"refresh_token": "dev-refresh"})
    assert r2.status_code == 200, r2.text
    assert r2.json()["id_token"] == "dev-refresh"
