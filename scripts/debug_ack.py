import tempfile, os, sys, json
from fastapi.testclient import TestClient
# setup temp db
tmp_dir = tempfile.mkdtemp()
db_file = os.path.join(tmp_dir, 'test_core.db')
print('db_file', db_file)
os.environ['CORE_DB_PATH']=db_file
# reload modules
for m in ('core.db','core.api','core.models','core.sync'):
    if m in sys.modules: del sys.modules[m]
from core.api import app
from core.db import init_db, SessionLocal
from core.models import OperationLog
import core.sync as syncmod
init_db()
client = TestClient(app)
# create existing op
db = SessionLocal()
try:
    op = OperationLog(user_id='u1', item_id='item1', op_type='conflict_seen', payload=json.dumps({}), created_at=None)
    db.add(op)
    db.commit()
finally:
    db.close()
# monkeypatch detect_conflicts
syncmod.detect_conflicts = lambda user_id, sa=None: ['item1','item2']
# call ack
r = client.post('/api/v1/sync/ack', json={'user_id':'u1','item_id':'item2','note':'seen'})
print('status',r.status_code)
print('text', r.text)
