from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "<b>Lingo</b> — Indonesian language tutor\n\n"
        "Команды:\n"
        "/help — справка\n"
        "/ping — проверка, что бот жив",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Как будет работать Lingo:</b>\n\n"
        "1) Карточки (SRS) — учим слова по интервальному повторению\n"
        "2) Уроки — грамматика + упражнения\n"
        "3) Практика — диалоги с AI\n\n"
        "Пока это базовый каркас. Дальше начнём с базы проекта и схемы данных.",
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")

