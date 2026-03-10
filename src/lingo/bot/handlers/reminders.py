from __future__ import annotations

import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository

router = Router(name="reminders")


_TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


@router.message(Command("remind_on"))
async def remind_on(message: Message, db: Database) -> None:
    if message.from_user is None:
        return
    repo = UserRepository(db)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return
    await repo.set_reminder_enabled(message.from_user.id, True)
    await message.answer(f"✅ Напоминания включены. Время: <b>{user.reminder_time}</b>")


@router.message(Command("remind_off"))
async def remind_off(message: Message, db: Database) -> None:
    if message.from_user is None:
        return
    repo = UserRepository(db)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return
    await repo.set_reminder_enabled(message.from_user.id, False)
    await message.answer("🛑 Напоминания выключены.")


@router.message(Command("remind_time"))
async def remind_time(message: Message, db: Database) -> None:
    if message.from_user is None:
        return
    repo = UserRepository(db)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Формат: <code>/remind_time HH:MM</code> (например <code>/remind_time 09:00</code>)")
        return

    hhmm = parts[1].strip()
    if not _TIME_RE.match(hhmm):
        await message.answer("Неверный формат времени. Используй <code>HH:MM</code> (00:00–23:59).")
        return

    await repo.set_reminder_time(message.from_user.id, hhmm)
    await repo.set_reminder_enabled(message.from_user.id, True)
    await message.answer(f"✅ Время напоминаний: <b>{hhmm}</b> (включено).")

