## Practice scenarios

Файлы в этой папке описывают сценарии для AI Practice (`/practice`).

### Формат JSON (`scenario-XX.json`)

Обязательные поля:
- `id`: строка (`scenario-01`)
- `title`: русское название
- `title_id`: indonesian/english short title
- `order`: число (для сортировки)
- `difficulty`: 1..3
- `estimated_time`: минуты
- `tags`: список строк
- `setting`: краткий контекст (RU)
- `roles`: роли (RU), кто студент и кто бот
- `goals`: список целей (RU)
- `must_use`: список слов/фраз, которые стоит попробовать (ID)
- `sample_dialog`: 4-8 реплик (минимум), с `role` (`student`/`tutor`) и `text`

### Использование

Сценарии загружаются в `/practice` и добавляются в системный prompt, чтобы AI держался темы.

