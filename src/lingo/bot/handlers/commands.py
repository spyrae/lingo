from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from lingo.bot.keyboards.reply import get_main_menu_keyboard

router = Router(name="commands")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Как будет работать Lingo:</b>\n\n"
        "1) Карточки (SRS) — учим слова по интервальному повторению\n"
        "2) Уроки — грамматика + упражнения\n"
        "3) Практика — диалоги с AI (Codex)\n\n"
        "Команды:\n"
        "/menu — главное меню\n"
        "/cards — карточки\n"
        "/lesson — уроки\n"
        "/practice — практика диалога\n"
        "/stop — остановить практику\n"
        "/ping — проверка, что бот жив",
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")

