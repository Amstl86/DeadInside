import sys
import os
os.environ['CORE_DB_PATH'] = os.path.abspath('./data/test.db')
for m in ('core.db','core.api','core.models','core.sync'):
    if m in sys.modules:
        del sys.modules[m]
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import core.api as api
import core.sync as sync
print('module core.sync is', sync)
print('module core.api.sync is', api.sync)
print('id(core.sync)==id(api.sync)?', id(sync)==id(api.sync))
print('detect_conflicts in core.sync ->', getattr(sync,'detect_conflicts',None))
print('detect_conflicts in core.api.sync ->', getattr(api.sync,'detect_conflicts',None))
print('ids: ', id(getattr(sync,'detect_conflicts',None)), id(getattr(api.sync,'detect_conflicts',None)))
