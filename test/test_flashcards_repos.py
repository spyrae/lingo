from pathlib import Path

import pytest

from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository
from lingo.memory.repositories.user_words_repository import UserWordsRepository
from lingo.memory.repositories.vocabulary_repository import VocabularyRepository
from lingo.services.srs import Quality


@pytest.mark.asyncio
async def test_can_insert_vocab_and_pick_new_word(tmp_path: Path) -> None:
    db = Database(tmp_path / "lingo.db")
    await db.connect()
    try:
        user = await UserRepository(db).create(telegram_id=1, level="beginner")
        vocab = VocabularyRepository(db)
        await vocab.insert_words(
            [
                {"indonesian": "selamat", "russian": "поздравляю", "category": "greetings"},
                {"indonesian": "makan", "russian": "есть", "category": "verbs"},
            ]
        )

        word_id = await vocab.get_random_new_word_id(user_id=user.id, category=None)
        assert word_id is not None
    finally:
        await db.disconnect()


@pytest.mark.asyncio
async def test_record_review_updates_user_word(tmp_path: Path) -> None:
    db = Database(tmp_path / "lingo.db")
    await db.connect()
    try:
        user = await UserRepository(db).create(telegram_id=1, level="beginner")
        vocab = VocabularyRepository(db)
        await vocab.insert_words(
            [{"indonesian": "air", "russian": "вода", "category": "food"}]
        )
        word_id = await vocab.get_random_new_word_id(user_id=user.id, category=None)
        assert word_id is not None

        uw = UserWordsRepository(db)
        await uw.ensure_user_word(user.id, word_id)
        res = await uw.record_review(user.id, word_id, Quality.CORRECT)
        assert res.new_repetitions == 1

        row = await db.fetchone(
            "SELECT repetitions, interval_days FROM user_words WHERE user_id = ? AND word_id = ?",
            (user.id, word_id),
        )
        assert row is not None
        assert row["repetitions"] == 1
        assert row["interval_days"] == 1
    finally:
        await db.disconnect()

