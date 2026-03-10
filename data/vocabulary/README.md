## Vocabulary seed

Файл `vocab-500.tsv` — базовый seed-словарь (500 слов) для таблицы `vocabulary`.

### Формат TSV

Колонки:
- `indonesian`
- `russian`
- `category` (одна из `WORD_CATEGORIES` в `src/lingo/memory/categories.py`)
- `difficulty` (1..3)
- `part_of_speech` (опционально)
- `english_gloss` (опционально, хранится в `notes` как `en: ...`)

### Импорт в SQLite

Команда (one-shot):

```bash
python -m lingo.content.seed_vocabulary
```

