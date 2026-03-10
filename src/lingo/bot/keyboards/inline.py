from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

