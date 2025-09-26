# Velayne

---

## 🇷🇺 О проекте / About

**Velayne** — Telegram-бот для автоматизации и симуляции алгоритмического трейдинга (Python 3.11+, aiogram 3.x, Pydantic v2, ONNX/ML, SQLAlchemy-async).

- Sandbox (демо): безопасная симуляция, все действия пишутся в датасеты
- Live: реальная торговля по вашим ключам (без права вывода)
- Каталог и студия стратегий (DSL, YAML, без eval)
- Модель ML обучается из трейдов и сигналов (Parquet)
- Поддержка многих бирж (binance, bybit, okx), подписки, ЮKassa, диагностика и админка
- Безопасность: шифрование ключей (Fernet), аудит, лог-редакция, GDPR-экспорт

**Дисклеймер:**  
Алготрейдинг — это эксперименты, не финансовый совет, риски не исключены.

---

## 🪄 Быстрый старт (Windows)

1. Установите Python 3.11+ и `git clone ...`
2. Скопируйте `.env.example` → `.env`, заполните TG_TOKEN, ADMIN_ID, ENCRYPTION_KEY
3. Дважды кликните `scripts/start.bat` — всё запустится в одном окне
4. Первый запуск — sandbox, selftest (`python -m velayne.run --selftest`)

---

## 🐧 Быстрый старт (Linux)

1. `bash scripts/install.sh` (venv + deps)
2. systemd: создайте velayne.service с  
   `ExecStart=/path/.venv/bin/python -m velayne.run`
3. `sudo systemctl start velayne.service`
4. Для диагностики: `python -m velayne.run --selftest`

---

## ⚡ Sandbox → Dataset → Training

- Все сигналы, сделки, фичи пишутся в Parquet (`data/trades/`, `data/features/`, `data/labels/`)
- ML-модель обучается автоматически (скользящее окно), метрики логируются
- Источники: sandbox/live (веса регулируются)
- Новости парсятся и классифицируются (News Guard: NONE/CAUTION/RED)

---

## 🚦 Live-режим

- /go_live — добавьте ключи (только торговля, без вывода)
- Выбор стратегий: рекомендованные/каталог DSL
- Воркеры в Live запускаются/останавливаются через /admin
- Рекомендации ML, sandbox-shadow для новых стратегий

---

## 💳 Подписки, тарифы и оплата

- /pay — оформление подписки через ЮKassa (если подключено)
- Тарифы: TEST (sandbox), BASIC, PRO, VIP
- Статус и управление — через /admin

---

## 📈 Новости, ML, метрики

- RSS-агрегация: CoinDesk, CoinTelegraph, Binance Announcements (офлайн-кеш)
- News Guard — влияет на риск/допуск к сделкам
- ML: ONNX, ensemble (rule-based + ML + volatility), blending весов
- Метрики доступны админу, selftest и финчек

---

## 🛠️ Админка и дашборд

- `/admin` — режимы, воркеры, диагностика, selftest, рассылка, очистка, экспорт
- `/dashboard` — мини-дашборд (FastAPI), инструкции по запуску/доступу
- Chaos-режим: имитация сбоев, деградация сети
- Алерты в ТГ админу (latency, circuit breaker)

---

## 🧪 Диагностика и финальная проверка

- Финальная проверка:  
  `scripts/final_gate.(bat|sh)` или `scripts/verify_all.(bat|sh)`  
  (прогоняет linters, selftest, bandit, pytest, package)
- Самотест:  
  `python -m velayne.run --selftest` — проверяет все сервисы

---

## ⚙️ .env и настройки

- TG_TOKEN, ADMIN_ID, ENCRYPTION_KEY (обязательно)
- EXCHANGE_TESTNET=true — использовать тестнет-биржи
- ORDER_QUEUE_MAX_PARALLEL=3, ORDER_QUEUE_MAX_PER_SEC=5 — лимиты ордеров
- LOG_RETENTION_DAYS, DATA_RETENTION_DAYS, ... — политики хранения
- DEFAULT_TZ=UTC — часовой пояс по умолчанию

---

## 🔒 Безопасность

- Ключи шифруются (Fernet), маскируются в логах
- RBAC: user/editor/admin, логирование операций, GDPR-экспорт через /export_my_data
- Bandit и secrets-скан для всего кода

---

## 🧑‍💻 Тесты и релиз

- Быстрый тест: `scripts/quickcheck.(bat|sh)`
- Финчек: `scripts/final_gate.(bat|sh)`
- Сборка: `scripts/package.(bat|sh)`
- CI: см. `.github/workflows/ci_github_actions.yml`
- Выпуск: все тесты/selftest/линтеры должны быть зелёными

---

## 📚 Документация

- [Оферта (RU)](docs/terms_ru.md)
- [Политика (RU)](docs/privacy_ru.md)
- [DSL-гайд](docs/dsl_guide.md)
- [FAQ, предложения: docs/offer_*, docs/faq_*]

---

## 🚀 Команды и стратегии

- Все команды: см. `velayne/scripts/gen_readme.py` или /help в боте
- Все стратегии: базовые + каталог DSL, /catalog, /submit_strategy

---

## 📝 Лицензия и контакты

- Лицензия: MIT
- Поддержка: support@velayne.io
- Telegram: https://t.me/velayne

---

## 🇬🇧 English (short)

**Velayne** — Telegram trading bot, full-featured sandbox and live trading, ONNX ML, secure keys, RBAC, subscriptions.

- One-click start: `scripts/start.bat` or `scripts/install.sh`
- All trades/signals stored in Parquet, ML auto-training
- Live: keys added via /go_live, strategies via DSL catalog or recommendations
- Admin: all control in `/admin`, diagnostics, dashboard, selftest
- Security: Fernet key encryption, GDPR export, audit, Bandit/secrets scan
- Full docs: see [DSL Guide](docs/dsl_guide.md), [Terms](docs/terms_ru.md), [Privacy](docs/privacy_ru.md)

---