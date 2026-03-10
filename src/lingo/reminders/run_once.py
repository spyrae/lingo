from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

from aiogram import Bot

from lingo.bot.main import create_bot
from lingo.config import Settings
from lingo.memory.database import Database
from lingo.memory.repositories.reminders_repository import RemindersRepository

logger = logging.getLogger(__name__)


REMINDER_TEXT = (
    "⏰ Мягкое напоминание: давай 5–10 минут на индонезийский?\n\n"
    "Команды:\n"
    "• /cards — карточки\n"
    "• /lesson — уроки\n"
    "• /practice — практика диалога\n"
)


async def send_reminders(*, bot: Bot, db: Database, now: datetime | None = None) -> int:
    """
    Send reminders to users whose reminder_time matches current HH:MM.

    Called by APScheduler every minute or standalone via `run_once()`.
    """
    repo = RemindersRepository(db)
    now_dt = now or datetime.now()
    today_iso = date.fromtimestamp(now_dt.timestamp()).isoformat()
    hhmm = now_dt.strftime("%H:%M")

    recipients = await repo.list_due_recipients(today_iso=today_iso, hhmm=hhmm)
    if not recipients:
        return 0

    sent = 0
    for r in recipients:
        try:
            await bot.send_message(chat_id=r.telegram_id, text=REMINDER_TEXT)
            await repo.mark_sent(user_id=r.user_id, today_iso=today_iso, hhmm=hhmm)
            sent += 1
        except Exception:
            logger.exception("Failed to send reminder to telegram_id=%s", r.telegram_id)

    if sent:
        logger.info("Sent %d reminders for %s %s", sent, today_iso, hhmm)
    return sent


async def run_once(*, now: datetime | None = None) -> int:
    """Standalone: create bot + db, send reminders, close."""
    settings = Settings()
    bot = create_bot(settings)
    db = Database(settings.db_path)
    try:
        await db.connect()
        return await send_reminders(bot=bot, db=db, now=now)
    finally:
        await db.disconnect()
        await bot.session.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(run_once())


if __name__ == "__main__":
    main()
