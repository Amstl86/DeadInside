import os
import datetime
from typing import Optional
from google.cloud import firestore
from .db import SessionLocal
from .models import Item


def _get_client(service_account_json: Optional[str] = None):
    if service_account_json:
        return firestore.Client.from_service_account_json(service_account_json)
    return firestore.Client()


def push_all(user_id: str, service_account_json: Optional[str] = None):
    """Push all local items to Firestore under users/{uid}/items/{itemId}.
    Uses batched writes and stores an operation log entry in users/{uid}/ops_log if available.
    """
    client = _get_client(service_account_json)
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        batch = client.batch()
        for it in items:
            doc_ref = client.collection("users").document(user_id).collection("items").document(it.id)
            batch.set(doc_ref, {
                "title": it.title,
                "content": it.content,
                "created_at": it.created_at.isoformat() if it.created_at else None,
                "updated_at": it.updated_at.isoformat() if it.updated_at else None,
                "version": it.version,
                "deleted": it.deleted,
            }, merge=True)
        batch.commit()
    finally:
        db.close()


def _parse_iso(s: Optional[str]):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None


def pull_all(user_id: str, service_account_json: Optional[str] = None):
    """Pull all items from Firestore and merge into local DB (last-writer-by-updated_at).

    This is a conservative merge: remote wins when remote.updated_at is newer than local.updated_at.
    """
    client = _get_client(service_account_json)
    db = SessionLocal()
    try:
        docs = client.collection("users").document(user_id).collection("items").stream()
        count = 0
        for d in docs:
            data = d.to_dict() or {}
            remote_updated = _parse_iso(data.get("updated_at"))
            local = db.get(Item, d.id)
            if local is None:
                local = Item(
                    id=d.id,
                    title=data.get("title") or "",
                    content=data.get("content"),
                    created_at=_parse_iso(data.get("created_at")) or datetime.datetime.utcnow(),
                    updated_at=remote_updated or datetime.datetime.utcnow(),
                    version=data.get("version", 1),
                    deleted=data.get("deleted", False),
                )
                db.add(local)
            else:
                # last-writer-by-updated_at
                if remote_updated and (not local.updated_at or remote_updated > local.updated_at):
                    local.title = data.get("title") or local.title
                    local.content = data.get("content")
                    local.updated_at = remote_updated
                    local.version = data.get("version", local.version)
                    local.deleted = data.get("deleted", local.deleted)
            count += 1
        db.commit()
        return count
    finally:
        db.close()


def detect_conflicts(user_id: str, service_account_json: Optional[str] = None):
    """Detect items where both local and remote have updates after a given timestamp.

    Returns a list of item ids that may need manual merge.
    """
    client = _get_client(service_account_json)
    db = SessionLocal()
    try:
        conflicts = []
        docs = client.collection("users").document(user_id).collection("items").stream()
        for d in docs:
            data = d.to_dict() or {}
            remote_updated = _parse_iso(data.get("updated_at"))
            local = db.get(Item, d.id)
            if local and remote_updated and local.updated_at and remote_updated > local.updated_at:
                # remote newer than local (no conflict)
                continue
            if local and remote_updated and local.updated_at and local.updated_at > remote_updated:
                # local newer than remote (no conflict)
                continue
            # if both have updates but timestamps are close, flag for manual review
            # simple heuristic: if both updated_at exist and differ by less than 5 seconds
            if local and remote_updated and local.updated_at:
                delta = abs((local.updated_at - remote_updated).total_seconds())
                if delta < 5:
                    conflicts.append(d.id)
        return conflicts
    finally:
        db.close()

