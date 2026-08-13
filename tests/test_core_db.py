import os
import sys
import importlib


def test_db_create_and_query(tmp_path, monkeypatch):
    db_file = tmp_path / "test_core.db"
    monkeypatch.setenv("CORE_DB_PATH", str(db_file))

    # ensure modules reloaded with new env
    for mod in ("core.db", "core.models"):
        if mod in sys.modules:
            del sys.modules[mod]

    import core.db as db_mod
    import core.models as models_mod
    importlib.reload(db_mod)
    importlib.reload(models_mod)

    from core.db import init_db, SessionLocal
    from core.models import Item

    init_db()
    s = SessionLocal()
    try:
        it = Item(title="hello", content="world")
        s.add(it)
        s.commit()

        r = s.query(Item).filter_by(title="hello").one()
        assert r.content == "world"
    finally:
        s.close()
