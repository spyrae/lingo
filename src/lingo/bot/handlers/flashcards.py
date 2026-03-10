from __future__ import annotations

import json
from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from lingo.bot.keyboards.inline import (
    get_category_keyboard,
    get_flashcard_rate_keyboard,
    get_flashcard_show_keyboard,
)
from lingo.gamification.achievement_manager import AchievementManager, format_achievement_unlocked
from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository
from lingo.memory.repositories.user_words_repository import UserWordsRepository
from lingo.memory.repositories.vocabulary_repository import VocabularyRepository
from lingo.services.srs import Quality

router = Router(name="flashcards")


def _render_examples(examples_json: str | None) -> str:
    if not examples_json:
        return ""
    try:
        items = json.loads(examples_json)
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, str) and first.strip():
                return f"\n\n<i>Пример:</i> {first.strip()}"
    except Exception:
        return ""
    return ""


async def _get_internal_user_id(db: Database, telegram_id: int) -> int | None:
    user = await UserRepository(db).get_by_telegram_id(telegram_id)
    return user.id if user else None


@router.message(Command("cards"))
@router.message(F.text == "📚 Карточки")
async def start_cards(message: Message, db: Database) -> None:
    if message.from_user is None:
        return

    user_repo = UserRepository(db)
    await user_repo.update_activity(message.from_user.id)

    internal_user_id = await _get_internal_user_id(db, message.from_user.id)
    if internal_user_id is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    due = await UserWordsRepository(db).get_due_cards(internal_user_id, limit=1)
    if due:
        await send_card(message, db=db, internal_user_id=internal_user_id, word_id=due[0].word_id)
        return

    await message.answer(
        "Слов на повтор нет. Давай начнём с новых.\n\nВыбери категорию:",
        reply_markup=get_category_keyboard(),
    )


@router.callback_query(F.data.startswith("cards:new:"))
async def cards_new(callback: CallbackQuery, db: Database) -> None:
    if callback.from_user is None or callback.message is None:
        return

    internal_user_id = await _get_internal_user_id(db, callback.from_user.id)
    if internal_user_id is None:
        await callback.message.answer("Сначала нажми /start и пройди онбординг.")
        await callback.answer()
        return

    category = callback.data.split(":")[-1]
    if category == "all":
        category = None

    vocab = VocabularyRepository(db)
    word_id = await vocab.get_random_new_word_id(user_id=internal_user_id, category=category)
    if word_id is None:
        await callback.message.edit_text(
            "Похоже, новых слов нет. (Словарь пока пустой или всё уже изучено.)"
        )
        await callback.answer()
        return

    await UserWordsRepository(db).ensure_user_word(internal_user_id, word_id)
    await send_card(callback.message, db=db, internal_user_id=internal_user_id, word_id=word_id, is_new=True)
    await callback.answer()


async def send_card(
    message: Message,
    *,
    db: Database,
    internal_user_id: int,
    word_id: int,
    is_new: bool = False,
) -> None:
    word = await VocabularyRepository(db).get_word_by_id(word_id)
    if word is None:
        await message.answer("Карточка не найдена.")
        return

    header = "🆕 <b>Новое слово</b>" if is_new else "📝 <b>Карточка</b>"
    await message.answer(
        f"{header}\n\n🇮🇩 <b>{word.indonesian}</b>\n\nЧто означает это слово?",
        reply_markup=get_flashcard_show_keyboard(word_id),
    )


@router.callback_query(F.data.startswith("card:show:"))
async def card_show(callback: CallbackQuery, db: Database) -> None:
    if callback.message is None:
        return

    word_id = int(callback.data.split(":")[-1])
    word = await VocabularyRepository(db).get_word_by_id(word_id)
    if word is None:
        await callback.answer("Не найдено")
        return

    examples = _render_examples(word.examples_json)
    notes = f"\n\n📝 {word.notes}" if word.notes else ""

    await callback.message.edit_text(
        f"🇮🇩 <b>{word.indonesian}</b>\n"
        f"🇷🇺 <b>{word.russian}</b>"
        f"{examples}"
        f"{notes}\n\n"
        "Оцени, насколько хорошо ты это знал (0–5):",
        reply_markup=get_flashcard_rate_keyboard(word_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("card:rate:"))
async def card_rate(callback: CallbackQuery, db: Database) -> None:
    if callback.from_user is None or callback.message is None:
        return

    parts = callback.data.split(":")
    quality = Quality(int(parts[2]))
    word_id = int(parts[3])

    internal_user_id = await _get_internal_user_id(db, callback.from_user.id)
    if internal_user_id is None:
        await callback.message.answer("Сначала нажми /start и пройди онбординг.")
        await callback.answer()
        return

    result = await UserWordsRepository(db).record_review(internal_user_id, word_id, quality)
    await UserRepository(db).add_xp(callback.from_user.id, result.xp_earned)

    unlocked = await AchievementManager(db).check_and_unlock(
        user_id=internal_user_id, telegram_id=callback.from_user.id
    )
    for a in unlocked:
        await callback.message.answer(format_achievement_unlocked(a))

    # Next: prefer due cards; otherwise offer new category selection.
    due = await UserWordsRepository(db).get_due_cards(internal_user_id, limit=1)
    if due:
        await send_card(callback.message, db=db, internal_user_id=internal_user_id, word_id=due[0].word_id)
        await callback.answer(f"+{result.xp_earned} XP" if result.xp_earned else "Записал")
        return

    today = date.today().isoformat()
    await callback.message.edit_text(
        f"✅ На сегодня всё! ({today})\n\nХочешь выучить ещё новое слово?",
        reply_markup=get_category_keyboard(),
    )
    await callback.answer(f"+{result.xp_earned} XP" if result.xp_earned else "Записал")


@router.callback_query(F.data == "card:next")
async def card_next(callback: CallbackQuery, db: Database) -> None:
    if callback.from_user is None or callback.message is None:
        return

    internal_user_id = await _get_internal_user_id(db, callback.from_user.id)
    if internal_user_id is None:
        await callback.message.answer("Сначала нажми /start и пройди онбординг.")
        await callback.answer()
        return

    due = await UserWordsRepository(db).get_due_cards(internal_user_id, limit=1)
    if due:
        await send_card(callback.message, db=db, internal_user_id=internal_user_id, word_id=due[0].word_id)
        await callback.answer()
        return

    await callback.message.edit_text("Выбери категорию новых слов:", reply_markup=get_category_keyboard())
    await callback.answer()

