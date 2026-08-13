# TODO — проект DeadInside

Список задач: отмечено выполненное, остальное — в работе или ожидает реализации.

- [x] Define cross-platform architecture and tech choices
- [x] Design & implement core data layer (models + SQLite)
- [x] Design sync protocol and choose backend (Firebase)
- [x] Implement desktop UI prototype (Tkinter/CustomTkinter entrypoint)
- [x] Implement Android UI prototype
- [x] Implement auth (Firebase/dev fallback + ID/refresh token handling)
- [ ] Implement sync logic with conflict resolution (CRDT/last-writer)
- [x] Packaging, CI/CD and distribution (local PyInstaller validation + Linux workflow)
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
Приоритеты (актуальные):

- Высокий: синхронизация с конфликтами, продакшн-конфиг Firebase Auth, проверка артефакта GitHub Actions.
- Средний: финальная security review, docs, подготовка release checklist.
- Низкий: расширенные тесты, оптимизация и поддержка Android/desktop для продакшн-сборки.

---
**Текущее состояние**

- [x] Core API и DB проходят unit tests в проектном venv.
- [x] Android prototype проходит `flutter analyze` и `flutter test`.
- [x] Desktop-версия собирается через PyInstaller локально.
- [ ] Требуется проверка GitHub Actions артефакта на Linux/WSL в реальном CI.

**Следующие шаги**

- [ ] Запустить CI workflow на GitHub и проверить артефакт `deadinside-linux`.
- [ ] Завершить продакшн-конфиг Firebase Auth и refresh-token flow.
- [ ] Реализовать полноценную sync-логике с конфликтами и дедупликацией.
- [ ] Провести security review, обновить docs и подготовить release checklist.

**Ключевые заметки**

- В локальном dev-режиме auth работает через безопасный fallback, чтобы тестировать API без Firebase credentials.
- Android prototype уже готов как базовый scaffold для дальнейшей интеграции с Firebase и Firestore.
- Desktop packaging проверен локально; маркетинговый и release этап зависит от GitHub Actions и финальной валидации на Linux.

