# TODO — проект DeadInside

Список задач: отмечено выполненное, остальное — в работе или ожидает реализации.

- [ ] Define cross-platform architecture and tech choices (in-progress)
- [x] Design & implement core data layer (models + SQLite)
- [x] Design sync protocol and choose backend (Google Drive API / Firebase)
- [ ] Implement desktop UI for Linux (prototype) (in-progress)
- [ ] Implement Android UI (prototype)
- [ ] Implement auth (OAuth2) and token handling (in-progress)
- [ ] Implement sync logic with conflict resolution (CRDT/last-writer) (in-progress)
- [ ] Packaging, CI/CD and distribution (Linux packages, Android APK) (in-progress)
- [ ] Tests, security review, and docs (in-progress)
- [x] Architectural sketch: Flutter vs Python UI
- [x] Component diagram + API endpoints for Flutter+Firebase
- [x] Implement local FastAPI REST for core
- [x] Implement Firestore sync client (push/pull)
- [x] Add export/import utilities (local)
- [x] Add Alembic migrations
- [x] Add unit tests for core (pytest)
- [x] Add GitHub Actions CI workflow

---
Приоритеты (рекомендация):

- Высокий: `Implement Android UI (prototype)`, `Implement desktop UI for Linux`.
- Средний: `Implement auth (OAuth2) и token handling`, `Implement sync logic`.
- Низкий: упаковка/дистрибуция и расширенные тесты/аудит.

Если нужно, могу автоматически отмечать пункты как выполненные при изменениях в репо.

---
**Где мы остановились (на сегодня)**

- Добавлен workflow сборки Linux (`.github/workflows/build_linux.yml`), требуется его запуск в GitHub Actions чтобы получить исполняемый артефакт в `dist/`.

**Следующие 3 шага (приоритетные)**

- [ ] Запустить CI workflow на GitHub и скачать/проверить артефакт `deadinside-linux` (проверить на Linux/WSL).
- [ ] Реализовать аутентификацию (Firebase Auth / OAuth2) в `core` и добавить обработку ID/refresh токенов.
- [ ] Начать прототип Android (Flutter): scaffold проекта, подключить `firebase_auth`, реализовать базовую синхронизацию с Firestore.

