# DeadInside — Трекер целей

Приложение для управления личными целями и задачами, построенное на современном GUI-фреймворке **CustomTkinter**.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 Описание

**DeadInside** — это десктопный трекер целей, который помогает вам ставить задачи, отслеживать прогресс и достигать результатов. Приложение поддерживает работу в нескольких окнах, детальное редактирование задач и имеет современный интерфейс.

### ✨ Особенности

- 🎯 Управление целями и задачами
- 📅 Интеграция с календарём (tkcalendar)
- 🌓 Автоматическое переключение светлой/тёмной темы (system theme)
- 🔒 Защита от множественного запуска (на Windows)
- 🚀 Возможность автозагрузки при старте системы
- 💾 Локальное хранение данных

---

## 🛠 Установка

### Требования

- Python 3.8 или выше
- Tk (обычно поставляется вместе с Python)

### Шаги установки

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd DeadInside
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

   Или вручную:
   ```bash
   pip install customtkinter tkcalendar
   ```

---

## 🚀 Запуск приложения

```bash
python main.py
```

---

## 📁 Структура проекта

```
DeadInside/
├── main.py              # Точка входа в приложение
├── requirements.txt     # Зависимости проекта
├── README.md           # Документация
├── data/
│   └── data_manager.py # Модуль для работы с данными
├── ui/
│   ├── main_window.py      # Главное окно приложения
│   ├── setup_window.py     # Окно настройки
│   ├── goal_detail.py      # Детали цели
│   └── generate_icon.py    # Скрипт генерации иконки
├── utils/
│   └── autostart.py     # Утилиты автозагрузки
└── icon.ico             # Иконка приложения
```

---

## 🧩 Сборка в исполняемый файл (.exe)

Для сборки приложения в `.exe` используйте **PyInstaller**:

1. Установите PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Соберите проект:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico --name="DeadInside" main.py
   ```

3. Готовый файл найдёте в папке `dist/`.

---

## 📋 Планы развития (Roadmap)

- [ ] Сборка под Linux (.deb, .AppImage)
- [ ] Поддержка английского языка (i18n)
- [ ] Облачная синхронизация данных
- [ ] Мобильная версия для Android

---

## 🤝 Вклад в проект

Приветствуются issues и pull requests! Если у вас есть идеи по улучшению — создайте issue в репозитории.

---

## 📄 Лицензия

MIT License

---

## 📞 Контакты

По вопросам и предложениям обращайтесь через Issues на GitHub.