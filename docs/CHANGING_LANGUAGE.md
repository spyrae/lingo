# Changing the Target Language

Lingo ships with Indonesian vocabulary and grammar by default, but you can adapt it for **any language pair**. This guide covers every step in detail.

## Overview

There are up to 5 things you may need to change:

| What | Required? | Difficulty |
|------|-----------|------------|
| 1. Environment variables | Yes | 2 minutes |
| 2. Vocabulary (word lists) | Yes | 30-60 min |
| 3. Grammar lessons | Optional | Depends on content |
| 4. Practice scenarios | Optional | 15 min per scenario |
| 5. UI language (bot menus) | Only if not Russian | 30-60 min |

## 1. Environment Variables

The bot reads language settings from environment variables. Update your `.env` file (or Docker environment / docker-compose.yml):

```bash
# Example: switching to Spanish
TARGET_LANGUAGE=Spanish
TARGET_LANGUAGE_NATIVE=испанский
TARGET_FLAG=🇪🇸
NATIVE_FLAG=🇷🇺
WELCOME_PHRASE=Bienvenido!
```

### What each variable does

| Variable | Purpose | Used in |
|----------|---------|---------|
| `TARGET_LANGUAGE` | Language name in English. Used in the AI tutor system prompt so the LLM knows which language to teach. | AI practice, system prompt |
| `TARGET_LANGUAGE_NATIVE` | Language name in the user's native language (Russian by default). Shown in bot messages like "Write a phrase in {language}". | Bot UI messages |
| `TARGET_FLAG` | Flag emoji shown next to words in the target language. | Flashcards, quizzes, reminders |
| `NATIVE_FLAG` | Flag emoji shown next to translations in the native language. | Flashcards, quizzes, reminders |
| `WELCOME_PHRASE` | A greeting in the target language, shown on `/start`. | Onboarding screen |

### Example configurations

| Language | TARGET_LANGUAGE | TARGET_LANGUAGE_NATIVE | TARGET_FLAG | WELCOME_PHRASE |
|----------|----------------|----------------------|-------------|----------------|
| Spanish | Spanish | испанский | 🇪🇸 | Bienvenido! |
| French | French | французский | 🇫🇷 | Bienvenue! |
| German | German | немецкий | 🇩🇪 | Willkommen! |
| Italian | Italian | итальянский | 🇮🇹 | Benvenuto! |
| Portuguese | Portuguese | португальский | 🇧🇷 | Bem-vindo! |
| Japanese | Japanese | японский | 🇯🇵 | ようこそ! |
| Korean | Korean | корейский | 🇰🇷 | 환영합니다! |
| Turkish | Turkish | турецкий | 🇹🇷 | Hosgeldiniz! |
| Chinese | Chinese | китайский | 🇨🇳 | 欢迎! |
| Arabic | Arabic | арабский | 🇸🇦 | !أهلاً وسهلاً |
| Hindi | Hindi | хинди | 🇮🇳 | स्वागत है! |
| English | English | английский | 🇬🇧 | Welcome! |
| Thai | Thai | тайский | 🇹🇭 | ยินดีต้อนรับ! |

If your native (UI) language is not Russian, also change `NATIVE_FLAG` and see [Section 5](#5-ui-language-advanced) for translating bot menus.

## 2. Vocabulary

This is the most important step. Without vocabulary, the bot has nothing to teach.

### Where vocabulary lives

All vocabulary is stored as **TSV (tab-separated) files** in the `data/vocabulary/` directory. The bot loads **all** `*.tsv` files from this directory when you run the seed command. You can have one big file or split into multiple files by topic.

### TSV format

The header row must be exactly:

```
indonesian	russian	category	difficulty	part_of_speech	english_gloss
```

> **Note:** The column names `indonesian` and `russian` are kept for database compatibility. Despite the names, `indonesian` is the **target language** column and `russian` is the **native language** column. This works for any language.

Each subsequent row is one word or phrase:

```
hola	привет	greetings	1	other	hello
```

Fields separated by **tabs** (not spaces).

### Column reference

| Column | Description | Valid values |
|--------|-------------|-------------|
| `indonesian` | Word or phrase in the **target language** | Any text |
| `russian` | Translation in the **native language** | Any text |
| `category` | Topic category (see table below) | `greetings`, `numbers`, `food`, etc. |
| `difficulty` | How hard the word is | `1` (easy), `2` (medium), `3` (hard) |
| `part_of_speech` | Grammatical category | `noun`, `verb`, `adj`, `adv`, `other` |
| `english_gloss` | English meaning (for your reference, not shown to users) | Any text |

### Step-by-step: creating your vocabulary

1. **Back up existing vocabulary** (optional):
   ```bash
   mkdir -p data/vocabulary/backup
   mv data/vocabulary/*.tsv data/vocabulary/backup/
   ```

2. **Create your TSV file.** Use any text editor or spreadsheet app (Google Sheets, Excel - export as TSV). Example for Spanish (`data/vocabulary/spanish.tsv`):

   ```
   indonesian	russian	category	difficulty	part_of_speech	english_gloss
   hola	привет	greetings	1	other	hello
   buenos dias	доброе утро	greetings	1	other	good morning
   gracias	спасибо	greetings	1	other	thank you
   por favor	пожалуйста	greetings	1	other	please
   si	да	phrases	1	other	yes
   no	нет	phrases	1	other	no
   agua	вода	food	1	noun	water
   cafe	кофе	food	1	noun	coffee
   casa	дом	nouns	1	noun	house
   comer	есть	verbs	1	verb	to eat
   hablar	говорить	verbs	1	verb	to speak
   grande	большой	adjectives	1	adj	big
   bueno	хороший	adjectives	1	adj	good
   uno	один	numbers	1	other	one
   dos	два	numbers	1	other	two
   ```

   > **Tip:** Start with 100-200 words. You can always add more files later - the bot loads all `*.tsv` files.

   > **Tip:** If using Google Sheets, put each column in a separate cell, then File > Download > Tab-separated values (.tsv).

3. **Delete old database and re-seed:**
   ```bash
   # Remove old database (user progress will be lost!)
   rm -f data/lingo.db

   # Seed vocabulary into a fresh database
   uv run python -m lingo.content.seed_vocabulary
   ```

   You should see output like:
   ```
   INFO lingo.content.seed_vocabulary: Seeded 15 words from spanish.tsv
   ```

4. **Restart the bot.** New vocabulary is now available.

### Available categories

These categories are built into the bot (defined in `src/lingo/memory/categories.py`). Use the `Key` value in your TSV:

| Key | Display Name | Icon | Good for |
|-----|-------------|------|----------|
| `greetings` | Greetings | 👋 | Hello, goodbye, please, thank you |
| `numbers` | Numbers | 🔢 | 1-100, ordinals |
| `food` | Food & Drinks | 🍽️ | Food items, restaurant vocabulary |
| `travel` | Travel | ✈️ | Airport, hotel, directions |
| `daily` | Daily Life | 🏠 | Household, routine activities |
| `verbs` | Verbs | 🏃 | Action words |
| `adjectives` | Adjectives | 🎨 | Descriptive words |
| `nouns` | Nouns | 📦 | General nouns |
| `phrases` | Phrases | 💬 | Common expressions, idioms |
| `questions` | Questions | ❓ | Question words, common questions |
| `time` | Time | ⏰ | Days, months, time expressions |
| `shopping` | Shopping | 🛒 | Prices, stores, transactions |
| `health` | Health | 🏥 | Body, medical, wellness |
| `nature` | Nature | 🌿 | Animals, plants, weather |
| `emotions` | Emotions | 😊 | Feelings, moods |
| `work` | Work | 💼 | Office, professions |
| `idioms` | Idioms | 🗣️ | Idiomatic expressions |

You can add custom categories by editing `src/lingo/memory/categories.py`:

```python
WORD_CATEGORIES = {
    # ... existing categories ...
    "sports": {"name": "Sports", "icon": "⚽"},
    "music": {"name": "Music", "icon": "🎵"},
}
```

### Adding vocabulary without losing progress

If the bot is already running and users have progress, you can add new words without resetting:

```bash
# Add a new TSV file
cp my-new-words.tsv data/vocabulary/

# Re-seed (only inserts new words, skips existing ones)
uv run python -m lingo.content.seed_vocabulary
```

The seed script uses `INSERT OR IGNORE`, so existing words and user progress are preserved.

## 3. Grammar Lessons

Grammar lessons are **Markdown files** in `data/grammar/`. Each file is one lesson displayed to the user via `/lesson`.

### Lesson file format

Filename: any `.md` file, e.g. `01-basic-greetings.md`. Files are sorted alphabetically, so use number prefixes for ordering.

Content: standard Markdown. Example for Spanish:

```markdown
# Basic Greetings

## Formal vs Informal

In Spanish, you use different greetings depending on formality:

- **Hola** - Hello (universal, any context)
- **Buenos dias** - Good morning (formal)
- **Buenas tardes** - Good afternoon (formal)
- **Buenas noches** - Good evening/night (formal)

## Common phrases

| Spanish | Translation |
|---------|------------|
| Mucho gusto | Nice to meet you |
| Como estas? | How are you? (informal) |
| Como esta usted? | How are you? (formal) |

## Practice

Try greeting someone at different times of day!
```

### Steps

1. Remove or back up existing lessons:
   ```bash
   mkdir -p data/grammar/backup
   mv data/grammar/*.md data/grammar/backup/
   ```

2. Add your own `.md` files to `data/grammar/`.

3. No database changes needed - lessons are loaded from files at runtime.

## 4. Practice Scenarios

Practice scenarios guide the AI conversation in `/practice` mode. They are **JSON files** in `data/practice/`.

### Scenario file format

Each JSON file defines one scenario:

```json
{
  "id": "cafe",
  "title": "At a Cafe",
  "description": "Ordering coffee and snacks",
  "level": "beginner",
  "setting": "You are a friendly waiter at a small cafe. The student is a tourist trying to order in the local language. Be patient and helpful.",
  "goals": [
    "Greet the waiter",
    "Order a drink and food",
    "Ask for the bill"
  ],
  "must_use": [
    "por favor",
    "la cuenta",
    "quiero"
  ],
  "sample_dialog": [
    {"role": "student", "text": "Hola, buenos dias!"},
    {"role": "tutor", "text": "Buenos dias! Bienvenido. Que desea tomar?"},
    {"role": "student", "text": "Quiero un cafe, por favor."},
    {"role": "tutor", "text": "Muy bien! Un cafe. Algo mas?"}
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (used internally) |
| `title` | Yes | Shown in scenario selection menu |
| `description` | Yes | Short description for the user |
| `level` | No | Difficulty hint for the AI |
| `setting` | Yes | System prompt context for the AI tutor |
| `goals` | Yes | Learning objectives for this scenario |
| `must_use` | No | Words/phrases the student should practice |
| `sample_dialog` | No | Example conversation to set the tone |

The AI tutor automatically uses the language set in `TARGET_LANGUAGE`. The `setting` field tells the AI what role to play.

### Steps

1. Remove or move existing scenarios:
   ```bash
   mkdir -p data/practice/backup
   mv data/practice/*.json data/practice/backup/
   ```

2. Create your own JSON files in `data/practice/`. Name them anything, e.g. `cafe.json`, `hotel.json`, `shopping.json`.

3. No restart needed - scenarios are loaded on each `/practice` command.

### Scenario ideas

Good scenarios for any language:
- Ordering food at a restaurant
- Checking into a hotel
- Asking for directions
- Shopping at a market
- Making a phone call
- Visiting a doctor
- Job interview
- Meeting new people at a party

## 5. UI Language (Advanced)

The bot's **UI messages** (button labels, prompts, error messages) are in **Russian** by default. The target language content (flashcards, quizzes) adapts automatically via env vars, but the surrounding UI stays in Russian.

If you want the bot UI in a different language, you need to edit the source code.

### Files to edit

| File | What it contains |
|------|-----------------|
| `src/lingo/bot/handlers/onboarding.py` | Welcome message, level selection prompts |
| `src/lingo/bot/handlers/flashcards.py` | "Show answer", "Rate your recall", card prompts |
| `src/lingo/bot/handlers/quiz.py` | "Correct!", "Wrong", quiz flow messages |
| `src/lingo/bot/handlers/practice.py` | "Choose a scenario", "Practice stopped" |
| `src/lingo/bot/handlers/commands.py` | `/help` text with command descriptions |
| `src/lingo/bot/handlers/stats.py` | Statistics display labels |
| `src/lingo/bot/handlers/reminders.py` | Reminder setup messages |
| `src/lingo/bot/handlers/lessons.py` | Lesson navigation messages |
| `src/lingo/bot/keyboards/reply.py` | Main menu button labels ("Flashcards", "Quiz", etc.) |
| `src/lingo/bot/keyboards/inline.py` | Inline button labels ("Show answer", "Next", etc.) |
| `src/lingo/memory/categories.py` | Category display names |
| `src/lingo/gamification/level_manager.py` | Level-up messages |
| `src/lingo/gamification/achievement_manager.py` | Achievement descriptions |
| `src/lingo/gamification/achievements_definitions.py` | Achievement names and texts |

### Example: changing a message

In `src/lingo/bot/handlers/flashcards.py`, find:

```python
await message.answer("Сначала нажми /start и пройди онбординг.")
```

Change to:

```python
await message.answer("Please press /start first to complete onboarding.")
```

### Example: changing button labels

In `src/lingo/bot/keyboards/reply.py`, find the button texts and replace:

```python
# Before (Russian)
KeyboardButton(text="📚 Карточки")

# After (English)
KeyboardButton(text="📚 Flashcards")
```

## Troubleshooting

### "No vocabulary found" after switching language

Make sure you:
1. Created TSV files in `data/vocabulary/`
2. Deleted the old database: `rm -f data/lingo.db`
3. Ran the seed: `uv run python -m lingo.content.seed_vocabulary`

### Quiz shows too few options

The quiz needs at least 4 words to generate answer options. Make sure your vocabulary has at least 10-20 words.

### AI practice responds in the wrong language

Check that `TARGET_LANGUAGE` is set correctly in your `.env`. The AI tutor uses this value in its system prompt. Restart the bot after changing env vars.

### Emojis or special characters don't display

Some terminals and text editors don't handle emoji well. Make sure your `.env` file is saved as **UTF-8**. The flag emojis (`🇪🇸`, `🇫🇷`, etc.) require UTF-8 encoding.

## Summary Checklist

- [ ] Set `TARGET_LANGUAGE`, `TARGET_FLAG`, `NATIVE_FLAG`, `TARGET_LANGUAGE_NATIVE`, `WELCOME_PHRASE` in `.env`
- [ ] Create vocabulary TSV files in `data/vocabulary/`
- [ ] Delete old `data/lingo.db` and re-seed with `uv run python -m lingo.content.seed_vocabulary`
- [ ] (Optional) Add grammar lessons as `.md` files in `data/grammar/`
- [ ] (Optional) Add practice scenarios as `.json` files in `data/practice/`
- [ ] (Optional) Translate UI strings if your native language is not Russian (see Section 5)
- [ ] Restart the bot
