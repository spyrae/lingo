from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from lingo.bot.keyboards.inline import (
    get_exercise_choice_keyboard,
    get_exercise_next_keyboard,
    get_lesson_theory_keyboard,
    get_lessons_list_keyboard,
)
from lingo.config import get_settings
from lingo.content.grammar_loader import GrammarLessonLoader
from lingo.gamification.achievement_manager import AchievementManager, format_achievement_unlocked
from lingo.memory.database import Database
from lingo.memory.repositories.lesson_progress_repository import LessonProgressRepository
from lingo.memory.repositories.user_repository import UserRepository

router = Router(name="lessons")


class LessonStates(StatesGroup):
    in_lesson = State()
    awaiting_text_answer = State()


@dataclass(frozen=True)
class ExerciseCheckResult:
    correct: bool
    correct_text: str
    explanation: str | None


def _lessons_dir() -> Path:
    return Path(get_settings().data_dir) / "grammar"


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


async def _get_internal_user_id(db: Database, telegram_id: int) -> int | None:
    user = await UserRepository(db).get_by_telegram_id(telegram_id)
    return user.id if user else None


@router.message(Command("lesson"))
@router.message(F.text == "📖 Уроки")
async def lessons_list(message: Message, db: Database, state: FSMContext) -> None:
    if message.from_user is None:
        return

    user_repo = UserRepository(db)
    await user_repo.update_activity(message.from_user.id)

    internal_user_id = await _get_internal_user_id(db, message.from_user.id)
    if internal_user_id is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    loader = GrammarLessonLoader(_lessons_dir())
    progress = LessonProgressRepository(db)
    completed = await progress.list_completed_lesson_ids(internal_user_id)
    available = loader.get_available(completed_ids=completed)

    if not available:
        await message.answer("🎉 Все доступные уроки пройдены! (Пока их мало.)")
        return

    lesson_ids = [m.id for m in available[:10]]
    titles = {m.id: f"📖 {m.title} (~{m.estimated_time} мин)" for m in available}

    await state.clear()
    await message.answer(
        f"📖 Уроки грамматики\n\nДоступно: {len(available)}\nПройдено: {len(completed)}\n\nВыбери урок:",
        reply_markup=get_lessons_list_keyboard(lesson_ids, titles),
    )


@router.callback_query(F.data == "lesson:back")
async def lessons_back(callback: CallbackQuery, db: Database, state: FSMContext) -> None:
    if callback.message is None:
        return
    await state.clear()
    # reuse list logic by calling handler-style function
    msg = callback.message
    await msg.answer("Ок. Открываю список уроков…")
    # We can't re-enter the previous handler easily without a Message from user; just show hint.
    await msg.answer("Нажми «📖 Уроки» или /lesson, чтобы открыть список.")
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:open:"))
async def lesson_open(callback: CallbackQuery, db: Database, state: FSMContext) -> None:
    if callback.from_user is None or callback.message is None:
        return

    await UserRepository(db).update_activity(callback.from_user.id)
    internal_user_id = await _get_internal_user_id(db, callback.from_user.id)
    if internal_user_id is None:
        await callback.message.answer("Сначала нажми /start и пройди онбординг.")
        await callback.answer()
        return

    lesson_id = callback.data.split(":")[-1]
    loader = GrammarLessonLoader(_lessons_dir())
    lesson = loader.load_lesson(lesson_id)
    if lesson is None:
        await callback.answer("Урок не найден", show_alert=True)
        return

    await LessonProgressRepository(db).start_lesson(internal_user_id, lesson_id)

    await state.set_state(LessonStates.in_lesson)
    await state.update_data(
        lesson_id=lesson_id,
        lesson=lesson,
        exercise_idx=0,
        correct=0,
        total=len(lesson["exercises"]),
    )

    theory = lesson["theory"]
    key_points = "\n".join([f"• {p}" for p in theory.get("key_points", [])])
    key_points_block = f"\n\n<b>Запомни:</b>\n{key_points}" if key_points else ""

    await callback.message.edit_text(
        f"📖 <b>{lesson['title']}</b>\n"
        f"<i>{lesson['title_id']}</i>\n\n"
        f"{theory['text']}"
        f"{key_points_block}",
        reply_markup=get_lesson_theory_keyboard(lesson_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:start_exercises:"))
async def lesson_start_exercises(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        return
    data = await state.get_data()
    lesson_id = str(data.get("lesson_id", ""))
    await _show_exercise(callback.message, state=state, lesson_id=lesson_id)
    await callback.answer()


async def _check_exercise(ex: dict, user_text: str | None, choice_idx: int | None) -> ExerciseCheckResult:
    ex_type = ex["type"]
    explanation = ex.get("explanation")

    if ex_type == "choice":
        if choice_idx is None:
            raise ValueError("choice_idx is required for choice exercises")
        correct_idx = int(ex["correct"])
        correct_text = str(ex["options"][correct_idx])
        return ExerciseCheckResult(
            correct=choice_idx == correct_idx,
            correct_text=correct_text,
            explanation=explanation,
        )

    if user_text is None:
        raise RuntimeError("text answer required")

    ans = _normalize(user_text)
    if ex_type == "fill":
        correct = _normalize(str(ex["answer"]))
        return ExerciseCheckResult(
            correct=ans == correct,
            correct_text=str(ex["answer"]),
            explanation=explanation,
        )

    if ex_type == "translate":
        canonical = _normalize(str(ex["indonesian"]))
        accept = [_normalize(a) for a in ex.get("accept", [])]
        accept.append(canonical)
        return ExerciseCheckResult(
            correct=ans in set(accept),
            correct_text=str(ex["indonesian"]),
            explanation=explanation,
        )

    raise ValueError(f"Unknown exercise type: {ex_type}")


async def _show_exercise(message: Message, *, state: FSMContext, lesson_id: str) -> None:
    data = await state.get_data()
    lesson = data["lesson"]
    idx = int(data["exercise_idx"])
    total = int(data["total"])

    if idx >= total:
        correct = int(data["correct"])
        score = round((correct / total) * 100) if total else 0
        await message.edit_text(
            f"🏁 <b>Урок завершён</b>\n\n"
            f"Результат: <b>{correct}/{total}</b> ({score}%)\n\n"
            "Нажми /lesson чтобы выбрать следующий урок.",
        )
        await state.clear()
        return

    ex = lesson["exercises"][idx]
    ex_type = ex["type"]
    header = f"✏️ <b>Упражнение {idx + 1}/{total}</b>\n\n{ex['question']}"

    if ex_type == "choice":
        await message.edit_text(
            header,
            reply_markup=get_exercise_choice_keyboard(idx, list(ex["options"])),
        )
        return

    # fill / translate: await text answer
    hint = ""
    if ex_type == "fill" and ex.get("hint"):
        hint = f"\n\n<i>Подсказка:</i> {ex['hint']}"
    prompt = "\n\nНапиши ответ сообщением."
    await message.edit_text(header + hint + prompt)
    await state.set_state(LessonStates.awaiting_text_answer)


@router.callback_query(F.data.startswith("lesson:choice:"))
async def lesson_choice(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        return

    parts = callback.data.split(":")
    exercise_idx = int(parts[2])
    choice_idx = int(parts[3])

    data = await state.get_data()
    lesson = data["lesson"]
    ex = lesson["exercises"][exercise_idx]
    result = await _check_exercise(ex, user_text=None, choice_idx=choice_idx)

    correct = int(data["correct"]) + (1 if result.correct else 0)
    await state.update_data(correct=correct, exercise_idx=exercise_idx + 1)

    expl = f"\n\n💡 {result.explanation}" if result.explanation else ""
    if result.correct:
        text = "✅ <b>Правильно!</b>" + expl
    else:
        text = f"❌ <b>Неправильно</b>\nПравильный ответ: <b>{result.correct_text}</b>" + expl

    lesson_id = str(data.get("lesson_id", ""))
    await callback.message.edit_text(text, reply_markup=get_exercise_next_keyboard(lesson_id))
    await callback.answer()


@router.message(LessonStates.awaiting_text_answer)
async def lesson_text_answer(message: Message, db: Database, state: FSMContext) -> None:
    if message.from_user is None:
        return

    data = await state.get_data()
    lesson = data["lesson"]
    idx = int(data["exercise_idx"])
    ex = lesson["exercises"][idx]

    result = await _check_exercise(ex, user_text=message.text or "", choice_idx=None)
    correct = int(data["correct"]) + (1 if result.correct else 0)
    await state.update_data(correct=correct, exercise_idx=idx + 1)

    expl = f"\n\n💡 {result.explanation}" if result.explanation else ""
    if result.correct:
        text = "✅ <b>Правильно!</b>" + expl
    else:
        text = f"❌ <b>Неправильно</b>\nПравильный ответ: <b>{result.correct_text}</b>" + expl

    lesson_id = str(data.get("lesson_id", ""))
    await message.answer(text, reply_markup=get_exercise_next_keyboard(lesson_id))
    await state.set_state(LessonStates.in_lesson)

    # If finished, mark completed.
    total = int(data["total"])
    if (idx + 1) >= total:
        internal_user_id = await _get_internal_user_id(db, message.from_user.id)
        if internal_user_id is not None:
            score = round((correct / total) * 100) if total else 0
            if score >= 70:
                await LessonProgressRepository(db).complete_lesson(internal_user_id, lesson_id, score)
                xp_reward = int(data["lesson"].get("xp_reward", 0))
                await UserRepository(db).add_xp(message.from_user.id, xp_reward)
                unlocked = await AchievementManager(db).check_and_unlock(
                    user_id=internal_user_id, telegram_id=message.from_user.id
                )
                for a in unlocked:
                    await message.answer(format_achievement_unlocked(a))


@router.callback_query(F.data.startswith("lesson:next:"))
async def lesson_next(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        return
    data = await state.get_data()
    lesson_id = str(data.get("lesson_id", ""))
    await _show_exercise(callback.message, state=state, lesson_id=lesson_id)
    await callback.answer()

