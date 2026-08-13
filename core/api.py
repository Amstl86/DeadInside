from fastapi import FastAPI, HTTPException
from fastapi import Depends
from pydantic import BaseModel
from typing import List
from .db import SessionLocal, init_db
from .models import Item
from . import sync
import os
try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    firebase_admin_available = True
except Exception:
    firebase_admin_available = False

app = FastAPI(title="DeadInside Core API")


class ItemIn(BaseModel):
    title: str
    content: str | None = None


class ItemOut(ItemIn):
    id: str
    created_at: str | None
    updated_at: str | None
    version: int
    deleted: bool


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/v1/items", response_model=List[ItemOut])
def list_items():
    db = SessionLocal()
    try:
        items = db.query(Item).filter(Item.deleted == False).all()
        return [ItemOut(**it.to_dict()) for it in items]
    finally:
        db.close()


@app.post("/api/v1/items", response_model=ItemOut)
def create_item(payload: ItemIn):
    db = SessionLocal()
    try:
        it = Item(title=payload.title, content=payload.content)
        db.add(it)
        db.commit()
        db.refresh(it)
        return ItemOut(**it.to_dict())
    finally:
        db.close()


@app.put("/api/v1/items/{item_id}", response_model=ItemOut)
def update_item(item_id: str, payload: ItemIn):
    db = SessionLocal()
    try:
        it = db.query(Item).get(item_id)
        if not it:
            raise HTTPException(status_code=404, detail="Not found")
        it.title = payload.title
        it.content = payload.content
        it.version = (it.version or 1) + 1
        db.commit()
        db.refresh(it)
        return ItemOut(**it.to_dict())
    finally:
        db.close()


@app.delete("/api/v1/items/{item_id}")
def delete_item(item_id: str):
    db = SessionLocal()
    try:
        it = db.query(Item).get(item_id)
        if not it:
            raise HTTPException(status_code=404, detail="Not found")
        it.deleted = True
        it.version = (it.version or 1) + 1
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()


@app.post("/api/v1/sync/push")
def sync_push(user_id: str):
    service_account = os.environ.get("SERVICE_ACCOUNT_JSON")
    sync.push_all(user_id, service_account)
    return {"status": "pushed"}


@app.post("/api/v1/sync/pull")
def sync_pull(user_id: str):
    service_account = os.environ.get("SERVICE_ACCOUNT_JSON")
    count = sync.pull_all(user_id, service_account)
    return {"status": "pulled", "count": count}


@app.post("/api/v1/verify_token")
def verify_token(id_token: str):
    """Verify Firebase ID token and return uid if valid."""
    if not firebase_admin_available:
        raise HTTPException(status_code=500, detail="firebase_admin not installed/configured")
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return {"uid": decoded.get("uid"), "claims": decoded}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/v1/export")
def export_local():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return {"items": [i.to_dict() for i in items]}
    finally:
        db.close()


@app.post("/api/v1/import")
def import_local(payload: dict):
    items = payload.get("items") or []
    db = SessionLocal()
    try:
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
        db.commit()
        return {"imported": len(items)}
    finally:
        db.close()
