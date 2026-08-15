from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List
from .db import SessionLocal, init_db
from .models import Item
from . import sync
import os
import json

from .models import OperationLog

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    firebase_admin_available = True
except Exception:
    firebase_admin_available = False

app = FastAPI(title="DeadInside Core API")
AUTH_MODE = os.environ.get("AUTH_MODE", "dev" if not firebase_admin_available else "firebase")


def _dev_token_response(token: str | None = None, uid: str | None = None):
    resolved_uid = uid or "dev-user"
    return {
        "uid": resolved_uid,
        "claims": {"uid": resolved_uid, "auth_mode": "dev", "token": token or "dev-token"},
    }


def _verify_token_payload(payload: dict[str, Any] | None = None):
    if payload is None:
        return None
    if isinstance(payload, dict):
        return payload.get("id_token") or payload.get("token")
    return None


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
        it = db.get(Item, item_id)
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
        it = db.get(Item, item_id)
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


@app.get("/api/v1/sync/conflicts")
def list_conflicts(user_id: str):
    """Return detected conflict ids and ops_log entries for a user."""
    service_account = os.environ.get("SERVICE_ACCOUNT_JSON")
    # detect conflicts via sync module
    conflicts = sync.detect_conflicts(user_id, service_account)
    db = SessionLocal()
    try:
        ops = db.query(OperationLog).filter(OperationLog.user_id == user_id).order_by(OperationLog.created_at.desc()).all()
        return {"conflicts": conflicts, "ops_log": [o.to_dict() for o in ops]}
    finally:
        db.close()


@app.post("/api/v1/sync/resolve")
def resolve_conflict(payload: dict | None = None):
    """Resolve a conflict by applying provided item data to local DB and recording an ops_log entry.

    Expected payload: {"user_id": "...", "item": { ...item fields... }, "note": "optional"}
    """
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a dict")
    user_id = payload.get("user_id")
    item_obj = payload.get("item")
    note = payload.get("note")
    if not user_id or not item_obj or not isinstance(item_obj, dict):
        raise HTTPException(status_code=400, detail="user_id and item are required")

    db = SessionLocal()
    try:
        item_id = item_obj.get("id")
        if not item_id:
            raise HTTPException(status_code=400, detail="item.id is required")
        it = db.get(Item, item_id)
        # apply (upsert)
        if it is None:
            it = Item(
                id=item_id,
                title=item_obj.get("title") or "",
                content=item_obj.get("content"),
                created_at=item_obj.get("created_at"),
                updated_at=item_obj.get("updated_at"),
                version=item_obj.get("version", 1),
                deleted=item_obj.get("deleted", False),
            )
            db.add(it)
        else:
            it.title = item_obj.get("title") or it.title
            it.content = item_obj.get("content")
            it.updated_at = item_obj.get("updated_at") or it.updated_at
            it.version = item_obj.get("version", it.version)
            it.deleted = item_obj.get("deleted", it.deleted)

        # record resolution in ops_log
        try:
            op = OperationLog(user_id=user_id, item_id=item_id, op_type="conflict_resolved", payload=json.dumps({"item": item_obj, "note": note}), created_at=datetime.datetime.utcnow())
            db.add(op)
        except Exception:
            pass

        db.commit()
        return {"status": "resolved", "item_id": item_id}
    finally:
        db.close()


@app.post("/api/v1/verify_token")
def verify_token(payload: dict | None = None):
    """Verify Firebase ID token and return uid if valid; fall back to dev auth when not configured."""
    id_token = _verify_token_payload(payload)
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token is required")

    if AUTH_MODE == "dev" or not firebase_admin_available:
        return _dev_token_response(token=id_token)

    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return {"uid": decoded.get("uid"), "claims": decoded}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/v1/refresh_token")
def refresh_token(payload: dict | None = None):
    refresh_token_value = (payload or {}).get("refresh_token") if isinstance(payload, dict) else None
    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    if AUTH_MODE == "dev" or not firebase_admin_available:
        return {"uid": "dev-user", "id_token": refresh_token_value, "refresh_token": refresh_token_value}

    try:
        decoded = firebase_auth.verify_id_token(refresh_token_value)
        return {"uid": decoded.get("uid"), "id_token": refresh_token_value, "refresh_token": refresh_token_value}
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
            it = db.get(Item, obj.get("id"))
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
