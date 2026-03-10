from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from lingo.config import Settings, get_settings
from lingo.content.practice_scenarios import PracticeScenarioLoader
from lingo.bot.keyboards.inline import get_practice_scenarios_keyboard
from lingo.gamification.achievement_manager import AchievementManager, format_achievement_unlocked
from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository
from lingo.services.codex_service import CodexService

router = Router(name="practice")


class PracticeStates(StatesGroup):
    choosing_scenario = State()
    chatting = State()


SYSTEM_PROMPT_TEMPLATE = """You are Lingo, an Indonesian language tutor for a Russian-speaking student.

Rules:
- Student messages can be in Indonesian, Russian, or mixed.
- Prefer replying in Indonesian appropriate to the student's level, then add Russian explanation.
- Be concise (2-4 short sentences).
- If the student makes a mistake: show ❌ (what's wrong), ✅ (correct), and a brief explanation in Russian.
- Introduce new words with Russian meaning in parentheses.

Student profile:
- Level: {level}

Scenario (optional):
{scenario_block}

Output format (plain text, no markdown tables):
🇮🇩 ...
🇷🇺 ...
💡 ... (optional)
"""


def _format_prompt(*, system: str, history: list[dict[str, str]], user_message: str) -> str:
    # Keep prompt readable and stable for CLI tools.
    lines: list[str] = []
    lines.append("SYSTEM:")
    lines.append(system)
    lines.append("")
    if history:
        lines.append("HISTORY:")
        for msg in history[-8:]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            lines.append(f"{role.upper()}: {content}")
        lines.append("")
    lines.append("USER:")
    lines.append(user_message)
    lines.append("")
    lines.append("ASSISTANT:")
    return "\n".join(lines)


def _scenario_block(scenario: dict[str, object] | None) -> str:
    if not scenario:
        return "- None"
    title = str(scenario.get("title", ""))
    setting = str(scenario.get("setting", ""))
    goals = scenario.get("goals") or []
    must_use = scenario.get("must_use") or []
    sample = scenario.get("sample_dialog") or []

    def bullet(items: list[object]) -> str:
        return "\n".join(f"- {str(x)}" for x in items[:8]) if items else "- (none)"

    sample_lines: list[str] = []
    if isinstance(sample, list):
        for t in sample[:6]:
            if isinstance(t, dict):
                role = str(t.get("role", "")).upper()
                text = str(t.get("text", ""))
                if role and text:
                    sample_lines.append(f"{role}: {text}")

    return "\n".join(
        [
            f"- Title: {title}",
            f"- Setting: {setting}",
            "- Goals:",
            bullet(list(goals) if isinstance(goals, list) else []),
            "- Must use (try to include naturally):",
            bullet(list(must_use) if isinstance(must_use, list) else []),
            "- Sample dialog style:",
            "\n".join(sample_lines) if sample_lines else "- (none)",
        ]
    )


@router.message(Command("practice"))
@router.message(F.text == "💬 Практика")
async def start_practice(message: Message, state: FSMContext, db: Database) -> None:
    if message.from_user is None:
        return

    repo = UserRepository(db)
    await repo.update_activity(message.from_user.id)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    unlocked = await AchievementManager(db).check_and_unlock(
        user_id=user.id, telegram_id=user.telegram_id, event="practice_started"
    )
    for a in unlocked:
        await message.answer(format_achievement_unlocked(a))

    scenarios_dir = Path(__file__).resolve().parents[4] / "data" / "practice"
    loader = PracticeScenarioLoader(scenarios_dir)
    metas = loader.list_metas()

    await state.set_state(PracticeStates.choosing_scenario)
    await state.update_data(
        history=[],
        level=user.level,
        practice_messages=0,
        scenario_id=None,
    )

    await message.answer(
        "💬 Практика.\n\nВыбери сценарий (или начни без сценария):",
        reply_markup=get_practice_scenarios_keyboard(metas),
    )


@router.callback_query(F.data.startswith("practice_scenario:"))
async def choose_scenario(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        return

    scenario_id = (callback.data or "").split(":", 1)[1].strip()
    if scenario_id == "none":
        await state.update_data(scenario_id=None)
    else:
        await state.update_data(scenario_id=scenario_id)

    await state.set_state(PracticeStates.chatting)
    await callback.message.answer(
        "✅ Сценарий выбран.\n\n"
        "Напиши фразу на индонезийском (или по-русски, если нужно).\n"
        "Чтобы закончить — /stop.",
    )
    await callback.answer()


@router.message(Command("stop"))
async def stop_practice(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("✅ Практика остановлена.")


@router.message(PracticeStates.chatting)
async def practice_chat(message: Message, state: FSMContext, db: Database) -> None:
    if message.from_user is None or not message.text:
        return

    data = await state.get_data()
    history: list[dict[str, str]] = list(data.get("history", []))
    level: str = str(data.get("level", "beginner"))
    scenario_id: str | None = data.get("scenario_id")

    settings: Settings = get_settings()
    codex = CodexService(
        command=settings.codex_command,
        timeout_seconds=settings.codex_timeout_seconds,
    )

    scenario = None
    if scenario_id:
        scenarios_dir = Path(__file__).resolve().parents[4] / "data" / "practice"
        scenario = PracticeScenarioLoader(scenarios_dir).load(scenario_id)

    system = SYSTEM_PROMPT_TEMPLATE.format(level=level, scenario_block=_scenario_block(scenario))
    prompt = _format_prompt(system=system, history=history, user_message=message.text)

    history.append({"role": "user", "content": message.text})
    await state.update_data(history=history)

    try:
        reply = await codex.chat(prompt=prompt)
    except Exception as e:
        await message.answer(f"❌ Ошибка Codex: {e}")
        return

    history.append({"role": "assistant", "content": reply})
    await state.update_data(history=history)
    await message.answer(reply)

    # XP: простая мотивация — 5 XP за каждое сообщение пользователя в практике
    practice_messages = int(data.get("practice_messages", 0)) + 1
    await state.update_data(practice_messages=practice_messages)
    await UserRepository(db).add_xp(message.from_user.id, 5)

