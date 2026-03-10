"""Quick quiz handler — random mini-tests for vocabulary practice.

Offers three quiz types:
1. translate_to_ru — Indonesian word → choose Russian translation
2. translate_to_id — Russian word → choose Indonesian translation
3. fill_category — guess the category of a word
"""

from __future__ import annotations

import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from lingo.gamification.achievement_manager import AchievementManager, format_achievement_unlocked
from lingo.gamification.level_manager import check_level_up, format_level_up
from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository

router = Router(name="quiz")

_NUM_OPTIONS = 4


async def _get_internal_user_id(db: Database, telegram_id: int) -> int | None:
    user = await UserRepository(db).get_by_telegram_id(telegram_id)
    return user.id if user else None


async def _pick_quiz(db: Database) -> dict | None:
    """Pick a random quiz question from vocabulary."""
    # Pick a target word
    target = await db.fetchone(
        "SELECT id, indonesian, russian, category FROM vocabulary ORDER BY RANDOM() LIMIT 1"
    )
    if not target:
        return None

    quiz_type = random.choice(["translate_to_ru", "translate_to_id"])

    if quiz_type == "translate_to_ru":
        # Show Indonesian → pick Russian
        wrong_rows = await db.fetchall(
            """
            SELECT russian FROM vocabulary
            WHERE id != ? AND russian != ?
            ORDER BY RANDOM() LIMIT ?
            """,
            (target["id"], target["russian"], _NUM_OPTIONS - 1),
        )
        options = [target["russian"]] + [r["russian"] for r in wrong_rows]
        random.shuffle(options)
        correct_idx = options.index(target["russian"])
        return {
            "question": f"🇮🇩 <b>{target['indonesian']}</b>\n\nКак переводится?",
            "options": options,
            "correct_idx": correct_idx,
            "word_id": target["id"],
            "xp": 15,
        }
    else:
        # Show Russian → pick Indonesian
        wrong_rows = await db.fetchall(
            """
            SELECT indonesian FROM vocabulary
            WHERE id != ? AND indonesian != ?
            ORDER BY RANDOM() LIMIT ?
            """,
            (target["id"], target["indonesian"], _NUM_OPTIONS - 1),
        )
        options = [target["indonesian"]] + [r["indonesian"] for r in wrong_rows]
        random.shuffle(options)
        correct_idx = options.index(target["indonesian"])
        return {
            "question": f"🇷🇺 <b>{target['russian']}</b>\n\nКак будет на индонезийском?",
            "options": options,
            "correct_idx": correct_idx,
            "word_id": target["id"],
            "xp": 15,
        }


def _build_quiz_keyboard(options: list[str], quiz_id: int) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(options):
        rows.append(
            [InlineKeyboardButton(text=opt, callback_data=f"quiz:answer:{quiz_id}:{i}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


# In-memory store for active quizzes (keyed by message_id or a counter)
_active_quizzes: dict[int, dict] = {}
_quiz_counter = 0


@router.message(Command("quiz"))
@router.message(F.text == "🧩 Квиз")
async def start_quiz(message: Message, db: Database) -> None:
    if message.from_user is None:
        return

    internal_user_id = await _get_internal_user_id(db, message.from_user.id)
    if internal_user_id is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    quiz = await _pick_quiz(db)
    if quiz is None:
        await message.answer("Словарь пуст. Сначала загрузи слова.")
        return

    global _quiz_counter
    _quiz_counter += 1
    quiz_id = _quiz_counter
    _active_quizzes[quiz_id] = quiz

    await message.answer(
        f"🧩 <b>Квиз</b>\n\n{quiz['question']}",
        reply_markup=_build_quiz_keyboard(quiz["options"], quiz_id),
    )


@router.callback_query(F.data.startswith("quiz:answer:"))
async def quiz_answer(callback: CallbackQuery, db: Database) -> None:
    if callback.from_user is None or callback.message is None:
        return

    parts = callback.data.split(":")
    quiz_id = int(parts[2])
    chosen_idx = int(parts[3])

    quiz = _active_quizzes.pop(quiz_id, None)
    if quiz is None:
        await callback.answer("Квиз устарел, начни новый: /quiz")
        return

    internal_user_id = await _get_internal_user_id(db, callback.from_user.id)
    correct = chosen_idx == quiz["correct_idx"]

    if correct:
        xp = quiz["xp"]
        await UserRepository(db).add_xp(callback.from_user.id, xp)
        text = f"✅ <b>Правильно!</b> +{xp} XP\n\n"
    else:
        correct_answer = quiz["options"][quiz["correct_idx"]]
        text = f"❌ <b>Неправильно.</b>\nПравильный ответ: <b>{correct_answer}</b>\n\n"

    if internal_user_id:
        unlocked = await AchievementManager(db).check_and_unlock(
            user_id=internal_user_id, telegram_id=callback.from_user.id
        )
        for a in unlocked:
            await callback.message.answer(format_achievement_unlocked(a))

        new_level = await check_level_up(db, callback.from_user.id)
        if new_level:
            await callback.message.answer(format_level_up(new_level))

    await callback.message.edit_text(
        text + "Ещё один?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🧩 Следующий вопрос", callback_data="quiz:next")],
                [InlineKeyboardButton(text="◀️ Хватит", callback_data="quiz:stop")],
            ]
        ),
    )
    await callback.answer("Верно!" if correct else "Неверно")


@router.callback_query(F.data == "quiz:next")
async def quiz_next(callback: CallbackQuery, db: Database) -> None:
    if callback.message is None:
        return

    quiz = await _pick_quiz(db)
    if quiz is None:
        await callback.message.edit_text("Словарь пуст.")
        await callback.answer()
        return

    global _quiz_counter
    _quiz_counter += 1
    quiz_id = _quiz_counter
    _active_quizzes[quiz_id] = quiz

    await callback.message.edit_text(
        f"🧩 <b>Квиз</b>\n\n{quiz['question']}",
        reply_markup=_build_quiz_keyboard(quiz["options"], quiz_id),
    )
    await callback.answer()


@router.callback_query(F.data == "quiz:stop")
async def quiz_stop(callback: CallbackQuery) -> None:
    if callback.message is None:
        return
    await callback.message.edit_text("Отлично потренировались! 💪\n\nНажми /quiz когда захочешь ещё.")
    await callback.answer()
