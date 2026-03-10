## Lingo — Indonesian Language Tutor Bot

Персональный Telegram-бот для изучения индонезийского языка: SRS-карточки, уроки грамматики и интерактивная практика.

### Быстрый старт (локально)

1) Скопируйте и заполните `.env`:

```bash
cp .env.example .env
```

2) Запустите модуль:

```bash
python -m lingo
```

### Переменные окружения

- `TELEGRAM_BOT_TOKEN`: токен бота от `@BotFather`
- `ALLOWED_USER_IDS`: JSON-массив Telegram user_id, которым разрешён доступ (например `[123]`)
- `ALLOW_ALL_USERS`: `true/false` — разрешить всем (не рекомендуется)

### Запуск в Docker

Собрать и запустить контейнер:

```bash
docker compose up --build -d
```

Нужно передать как минимум:

- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY` (для Codex-практики)

Пример:

```bash
TELEGRAM_BOT_TOKEN=xxx \
OPENAI_API_KEY=yyy \
docker compose up --build
```


