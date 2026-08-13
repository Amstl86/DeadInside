import json
from typing import List
from .db import SessionLocal, init_db
from .models import Item


def export_to_file(path: str):
    init_db()
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        data = [i.to_dict() for i in items]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"items": data}, f, ensure_ascii=False, indent=2)
        return path
    finally:
        db.close()


def import_from_file(path: str) -> int:
    init_db()
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    items = payload.get("items") or []
    db = SessionLocal()
    try:
        count = 0
        for obj in items:
            it = db.query(Item).get(obj.get("id"))
            if it is None:
                it = Item(
                    id=obj.get("id"),
                    title=obj.get("title") or "",
                    content=obj.get("content"),
                    created_at=obj.get("created_at"),
                    updated_at=obj.get("updated_at"),
                    version=obj.get("version", 1),
                    deleted=obj.get("deleted", False),
                )
                db.add(it)
                count += 1
        db.commit()
        return count
    finally:
        db.close()
