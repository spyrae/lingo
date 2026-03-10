from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 Карточки"),
                KeyboardButton(text="📖 Уроки"),
            ],
            [
                KeyboardButton(text="🧩 Квиз"),
                KeyboardButton(text="💬 Практика"),
            ],
            [
                KeyboardButton(text="📊 Прогресс"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие…",
    )

