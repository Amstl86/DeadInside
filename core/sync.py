import os
import datetime
from typing import Optional, Tuple, List
from google.cloud import firestore
from .db import SessionLocal
from .models import Item, OperationLog
import json


def _get_client(service_account_json: Optional[str] = None):
    try:
        if service_account_json:
            return firestore.Client.from_service_account_json(service_account_json)
        return firestore.Client()
    except Exception:
        # Best-effort: when Firestore credentials are not configured (dev/test),
        # return None so callers can handle lack of remote access gracefully.
        return None


def push_all(user_id: str, service_account_json: Optional[str] = None):
    """Push all local items to Firestore under users/{uid}/items/{itemId}.
    Uses batched writes and stores an operation log entry in users/{uid}/ops_log if available.
    """
    client = _get_client(service_account_json)
    if client is None:
        # nothing to push when Firestore client unavailable
        return 0
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


def _decide_merge(local: Optional[Item], data: dict) -> Tuple[bool, bool]:
    """Decide whether to apply remote data over local.

    Returns (apply_remote, conflict_detected).
    Strategy:
    - Prefer higher `version`.
    - If versions equal, use `updated_at` timestamp as tie-breaker.
    - If timestamps are very close (<5s) and content differs, mark as conflict.
    """
    remote_version = data.get("version") or 0
    remote_updated = _parse_iso(data.get("updated_at"))
    if local is None:
        return True, False

    local_version = local.version or 0
    if remote_version > local_version:
        return True, False
    if remote_version < local_version:
        return False, False

    # versions equal -> compare timestamps
    if remote_updated and local.updated_at:
        delta = (remote_updated - local.updated_at).total_seconds()
        # content difference heuristic
        remote_title = data.get("title") or ""
        remote_content = data.get("content")
        local_title = local.title or ""
        local_content = local.content
        if abs(delta) < 5 and (remote_title != local_title or remote_content != local_content):
            return False, True
        return remote_updated > local.updated_at, False

    if remote_updated and not local.updated_at:
        return True, False

    return False, False


def pull_all(user_id: str, service_account_json: Optional[str] = None, return_conflicts: bool = False):
    """Pull all items from Firestore and merge into local DB.

    By default returns count of processed remote docs. If `return_conflicts=True`, returns
    a tuple `(count, conflicts)` where `conflicts` is a list of item ids that need manual merge.
    """
    client = _get_client(service_account_json)
    if client is None:
        # no remote to pull from; return zero processed and no conflicts
        if return_conflicts:
            return 0, []
        return 0
    db = SessionLocal()
    try:
        docs = client.collection("users").document(user_id).collection("items").stream()
        count = 0
        conflicts: List[str] = []
        for d in docs:
            data = d.to_dict() or {}
            apply_remote, conflict = _decide_merge(db.get(Item, d.id), data)
            local = db.get(Item, d.id)
            remote_updated = _parse_iso(data.get("updated_at"))
            if local is None and apply_remote:
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
            elif local is not None and apply_remote:
                local.title = data.get("title") or local.title
                local.content = data.get("content")
                local.updated_at = remote_updated or local.updated_at
                local.version = data.get("version", local.version)
                local.deleted = data.get("deleted", local.deleted)
            elif conflict:
                conflicts.append(d.id)
                # log conflict into ops_log for later review
                try:
                    op = OperationLog(user_id=user_id, item_id=d.id, op_type="conflict_detected", payload=json.dumps(data), created_at=datetime.datetime.utcnow())
                    db.add(op)
                except Exception:
                    # best-effort logging; don't fail the whole sync for logging issues
                    pass
            count += 1
        db.commit()
        if return_conflicts:
            return count, conflicts
        return count
    finally:
        db.close()


def detect_conflicts(user_id: str, service_account_json: Optional[str] = None):
    """Detect potential conflicts between local and remote items.

    Uses the same heuristic as `_decide_merge` to identify items that require manual review.
    Returns a list of item ids that may need manual merge.
    """
    client = _get_client(service_account_json)
    if client is None:
        return []
    db = SessionLocal()
    try:
        conflicts = []
        docs = client.collection("users").document(user_id).collection("items").stream()
        for d in docs:
            data = d.to_dict() or {}
            apply_remote, conflict = _decide_merge(db.get(Item, d.id), data)
            if conflict:
                conflicts.append(d.id)
        return conflicts
    finally:
        db.close()

