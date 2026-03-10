import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from lingo.config import Settings
from lingo.bot.middlewares.db import DbMiddleware
from lingo.memory.database import Database

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    from lingo.bot.handlers import commands, flashcards, lessons, menu, onboarding, practice

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(onboarding.router)
    dp.include_router(commands.router)
    dp.include_router(flashcards.router)
    dp.include_router(lessons.router)
    dp.include_router(practice.router)
    dp.include_router(menu.router)
    return dp


MiddlewareHandler = Callable[[Update, dict[str, Any]], Awaitable[Any]]
MiddlewareType = Callable[[MiddlewareHandler, Update, dict[str, Any]], Awaitable[Any]]


def create_auth_middleware(settings: Settings) -> MiddlewareType:
    async def auth_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        if settings.allow_all_users:
            return await handler(event, data)

        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        if not settings.allowed_user_ids:
            logger.warning(
                "Access denied: no allowed_user_ids configured and allow_all_users is False"
            )
            return None

        if user and user.id not in settings.allowed_user_ids:
            logger.warning("Unauthorized access attempt from user %s", user.id)
            return None

        return await handler(event, data)

    return auth_middleware


async def run_bot(settings: Settings) -> None:
    bot = create_bot(settings)
    dp = create_dispatcher()
    dp.update.middleware(create_auth_middleware(settings))

    logger.info("Starting bot polling...")
    db = Database(settings.db_path)
    try:
        await db.connect()
        dp.update.middleware(DbMiddleware(db))
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.disconnect()
        await bot.session.close()

