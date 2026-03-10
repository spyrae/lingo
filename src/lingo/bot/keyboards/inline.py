from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lingo.memory.categories import WORD_CATEGORIES


def get_level_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌱 Полный ноль",
                    callback_data="onboarding:level:zero",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 Знаю базовые фразы",
                    callback_data="onboarding:level:beginner",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📖 Могу строить предложения",
                    callback_data="onboarding:level:elementary",
                )
            ],
        ]
    )


def get_goal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="5 слов", callback_data="onboarding:goal:5"),
                InlineKeyboardButton(text="10 слов", callback_data="onboarding:goal:10"),
            ],
            [
                InlineKeyboardButton(text="15 слов", callback_data="onboarding:goal:15"),
                InlineKeyboardButton(text="20 слов", callback_data="onboarding:goal:20"),
            ],
        ]
    )


def get_flashcard_show_keyboard(word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👀 Показать перевод", callback_data=f"card:show:{word_id}")],
            [InlineKeyboardButton(text="⏭️ Дальше", callback_data="card:next")],
        ]
    )


def get_flashcard_rate_keyboard(word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ 0", callback_data=f"card:rate:0:{word_id}"),
                InlineKeyboardButton(text="1", callback_data=f"card:rate:1:{word_id}"),
                InlineKeyboardButton(text="2", callback_data=f"card:rate:2:{word_id}"),
            ],
            [
                InlineKeyboardButton(text="😐 3", callback_data=f"card:rate:3:{word_id}"),
                InlineKeyboardButton(text="👍 4", callback_data=f"card:rate:4:{word_id}"),
                InlineKeyboardButton(text="🎯 5", callback_data=f"card:rate:5:{word_id}"),
            ],
        ]
    )


def get_category_keyboard() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for key, cat in sorted(WORD_CATEGORIES.items(), key=lambda x: int(x[1]["order"])):  # type: ignore[index]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{cat['icon']} {cat['name']}",
                    callback_data=f"cards:new:{key}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="🎲 Все категории", callback_data="cards:new:all")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lessons_list_keyboard(lesson_ids: list[str], titles: dict[str, str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for lesson_id in lesson_ids:
        title = titles.get(lesson_id, lesson_id)
        rows.append(
            [InlineKeyboardButton(text=title, callback_data=f"lesson:open:{lesson_id}")]
        )
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="lesson:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_lesson_theory_keyboard(lesson_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ К упражнениям",
                    callback_data=f"lesson:start_exercises:{lesson_id}",
                )
            ],
            [InlineKeyboardButton(text="◀️ К списку уроков", callback_data="lesson:back")],
        ]
    )


def get_exercise_choice_keyboard(exercise_idx: int, options: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for i, opt in enumerate(options):
        rows.append(
            [
                InlineKeyboardButton(
                    text=opt,
                    callback_data=f"lesson:choice:{exercise_idx}:{i}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_exercise_next_keyboard(lesson_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Далее", callback_data=f"lesson:next:{lesson_id}")],
        ]
    )

