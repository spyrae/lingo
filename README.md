# Lingo - Language Learning Telegram Bot

A personal Telegram bot for learning any foreign language. Features SRS flashcards (SM-2 algorithm), grammar lessons, AI-powered conversation practice, quizzes, achievements, and daily reminders.

Built with Python, aiogram 3, and SQLite. Runs anywhere with Docker.

## Features

- **SRS Flashcards** - spaced repetition with SM-2 algorithm, quality ratings 0-5
- **Grammar Lessons** - structured lessons loaded from Markdown files
- **AI Practice** - conversational practice powered by OpenAI (GPT-4.1-nano by default)
- **Quizzes** - multiple-choice vocabulary tests with XP rewards
- **Gamification** - XP, levels, streaks, achievements
- **Daily Reminders** - configurable reminder time with Word of the Day
- **Any Language** - fully configurable target language via environment variables

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- OpenAI API key (for AI practice feature)

### Local Setup

```bash
# Clone the repo
git clone https://github.com/yourname/lingo.git
cd lingo

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your tokens

# Install dependencies
uv sync

# Seed vocabulary (first run)
uv run python -m lingo.content.seed_vocabulary

# Start the bot
uv run python -m lingo
```

### Docker

```bash
# Build and run
docker compose up --build -d

# Or with inline env vars
TELEGRAM_BOT_TOKEN=xxx OPENAI_API_KEY=yyy docker compose up --build -d
```

Data persists in `./data/` (SQLite database, vocabulary).

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `OPENAI_API_KEY` | Yes* | - | OpenAI key (only for /practice) |
| `OPENAI_MODEL` | No | `gpt-4.1-nano` | OpenAI model name |
| `OPENAI_TIMEOUT_SECONDS` | No | `60` | AI request timeout |
| `DB_PATH` | No | `data/lingo.db` | SQLite database path |
| `DATA_DIR` | No | `data` | Content directory |
| `ALLOWED_USER_IDS` | No | `[]` | JSON array of allowed Telegram user IDs |
| `ALLOW_ALL_USERS` | No | `false` | Allow all users (not recommended) |
| `TARGET_LANGUAGE` | No | `Indonesian` | Target language in English |
| `TARGET_LANGUAGE_NATIVE` | No | `индонезийский` | Target language in user's native language |
| `TARGET_FLAG` | No | `🇮🇩` | Flag emoji for target language |
| `NATIVE_FLAG` | No | `🇷🇺` | Flag emoji for native language |
| `WELCOME_PHRASE` | No | `Selamat datang!` | Welcome phrase in target language |

*The bot works without `OPENAI_API_KEY`, but `/practice` (AI conversation) will be unavailable.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Onboarding / main menu |
| `/cards` | SRS flashcards |
| `/lesson` | Grammar lesson |
| `/practice` | AI conversation practice |
| `/quiz` | Vocabulary quiz |
| `/stats` | Progress and statistics |
| `/reminder` | Set daily reminder |
| `/help` | List commands |

## Changing the Target Language

The bot ships with Indonesian vocabulary and grammar, but you can switch to any language. See [docs/CHANGING_LANGUAGE.md](docs/CHANGING_LANGUAGE.md) for a step-by-step guide.

## Project Structure

```
lingo/
├── src/lingo/
│   ├── bot/              # Telegram bot (aiogram 3)
│   │   ├── handlers/     # Command and callback handlers
│   │   ├── keyboards/    # Inline and reply keyboards
│   │   ├── middlewares/   # Auth, DB injection
│   │   └── storage.py    # SQLite-backed FSM storage
│   ├── content/          # Content loaders (grammar, vocabulary, scenarios)
│   ├── gamification/     # XP, levels, achievements
│   ├── memory/           # Database, repositories
│   ├── reminders/        # Daily reminder scheduler
│   └── services/         # External API clients (OpenAI)
├── data/
│   ├── grammar/          # Markdown grammar lessons
│   ├── vocabulary/       # TSV word lists
│   └── practice/         # JSON practice scenarios
├── test/                 # Tests (pytest)
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest test/ -q

# Lint
uv run ruff check src/

# Type check
uv run mypy src/lingo/
```

## How It Works

**Spaced Repetition (SM-2):** Each flashcard tracks easiness factor, interval, and repetition count. After reviewing a card, you rate your recall (0-5). The algorithm schedules the next review accordingly - well-known cards appear less frequently.

**Gamification:** Every activity earns XP. Accumulate XP to level up (zero -> beginner -> elementary -> intermediate -> advanced). Unlock achievements for milestones like reviewing 100 words or completing 10 lessons.

**AI Practice:** The `/practice` command starts a conversation with an AI tutor. Choose a scenario (at a cafe, asking directions, etc.) or free talk. The tutor corrects mistakes and introduces new vocabulary in context.

## License

MIT
