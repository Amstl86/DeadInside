import os, sys, json, pathlib
from fastapi.testclient import TestClient
# setup project path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
# env
import tempfile
tmp = tempfile.mkdtemp()
os.environ['CORE_DB_PATH'] = os.path.join(tmp, 'test_core.db')
# reload modules
for m in ('core.db','core.api','core.models','core.sync'):
    if m in sys.modules: del sys.modules[m]
import core.api as api
from core.db import init_db, SessionLocal
from core.models import OperationLog
import core.sync as syncmod
print('before init_db, sync.detect_conflicts is', syncmod.detect_conflicts)
init_db()
client = TestClient(api.app)
# create op
db = SessionLocal()
try:
    op = OperationLog(user_id='u1', item_id='item1', op_type='conflict_seen', payload=json.dumps({}), created_at=None)
    db.add(op)
    db.commit()
finally:
    db.close()
# monkeypatch detect_conflicts
syncmod.detect_conflicts = lambda user_id, sa=None: ['item1','item2']
print('after monkeypatch, sync.detect_conflicts is', syncmod.detect_conflicts)
# call endpoint
r = client.get('/api/v1/sync/conflicts', params={'user_id':'u1'})
print('status', r.status_code)
print('body', r.json())
