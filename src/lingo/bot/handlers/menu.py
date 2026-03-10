from aiogram import F, Router
from aiogram.types import Message

router = Router(name="menu")


@router.message(F.text == "📚 Карточки")
async def open_flashcards(message: Message) -> None:
    await message.answer("Скоро здесь будут карточки (SRS).")


@router.message(F.text == "📖 Уроки")
async def open_lessons(message: Message) -> None:
    await message.answer("Открой /lesson, чтобы выбрать урок.")


@router.message(F.text == "💬 Практика")
async def open_practice(message: Message) -> None:
    await message.answer("Скоро здесь будет практика диалогов с AI.")


@router.message(F.text == "📊 Прогресс")
async def open_progress(message: Message) -> None:
    await message.answer("Скоро здесь будет прогресс и статистика.")

