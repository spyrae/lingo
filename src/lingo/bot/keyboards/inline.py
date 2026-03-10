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

