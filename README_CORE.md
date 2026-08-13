Core service (local) — quickstart

Requirements:
- Python 3.9+
- Install dependencies: `pip install fastapi uvicorn sqlalchemy pydantic google-cloud-firestore python-dotenv`

Environment:
- `SERVICE_ACCOUNT_JSON` (optional): path to Firebase service account JSON for server-side Firestore access.
- `CORE_DB_PATH` (optional): path to sqlite database file (default: `data/core.db`).

Run locally (development):

```bash
pip install -r requirements.txt
# then
uvicorn core.api:app --reload --host 127.0.0.1 --port 5000
```

Endpoints: see `/api/v1/*` in `core/api.py`.

Migrations (Alembic):

```bash
# generate env and run (first-time)
pip install -r requirements-dev.txt
alembic upgrade head
```

Tests:

```bash
pip install -r requirements-dev.txt
pytest -q
```

