from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from lingo.bot.keyboards.inline import get_goal_keyboard, get_level_selection_keyboard
from lingo.bot.keyboards.reply import get_main_menu_keyboard
from lingo.config import Settings
from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository

router = Router(name="onboarding")


class OnboardingStates(StatesGroup):
    selecting_level = State()
    setting_goal = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database, settings: Settings) -> None:
    if message.from_user is None:
        return

    repo = UserRepository(db)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer(
            f"{settings.target_flag} <b>{settings.welcome_phrase}</b> Добро пожаловать в Lingo.\n\n"
            "Давай настроим обучение. Какой у тебя уровень?",
            reply_markup=get_level_selection_keyboard(),
        )
        await state.set_state(OnboardingStates.selecting_level)
        return

    await message.answer(
        f"С возвращением!\n\n"
        f"Уровень: <b>{user.level}</b>\n"
        f"XP: <b>{user.total_xp}</b>\n"
        f"Streak: <b>{user.current_streak}</b> дней\n\n"
        "Что будем делать сегодня?",
        reply_markup=get_main_menu_keyboard(),
    )
    await state.clear()


@router.callback_query(
    OnboardingStates.selecting_level,
    F.data.startswith("onboarding:level:"),
)
async def process_level_selection(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if callback.from_user is None:
        return

    level = callback.data.split(":")[-1]
    repo = UserRepository(db)
    await repo.get_or_create(callback.from_user.id, default_level=level)

    await callback.message.edit_text(
        "Отлично. Сколько новых слов в день хочешь учить?",
        reply_markup=get_goal_keyboard(),
    )
    await state.set_state(OnboardingStates.setting_goal)
    await callback.answer()


@router.callback_query(
    OnboardingStates.setting_goal,
    F.data.startswith("onboarding:goal:"),
)
async def process_goal_selection(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if callback.from_user is None:
        return

    goal_str = callback.data.split(":")[-1]
    goal = int(goal_str)

    repo = UserRepository(db)
    await repo.update_daily_goal(callback.from_user.id, goal)

    await callback.message.edit_text(
        f"🎯 Цель: <b>{goal}</b> новых слов в день.\n\n"
        "Готово. Выбери, с чего начать:",
    )
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    await state.clear()
    await callback.answer()

