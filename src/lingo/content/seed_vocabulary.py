from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from lingo.config import Settings
from lingo.content.vocabulary_loader import VocabularyLoader
from lingo.memory.database import Database
from lingo.memory.repositories.vocabulary_repository import VocabularyRepository

logger = logging.getLogger(__name__)


DEFAULT_TSV_PATH = Path(__file__).resolve().parents[3] / "data" / "vocabulary" / "vocab-500.tsv"


async def seed_vocabulary(*, tsv_path: Path = DEFAULT_TSV_PATH) -> int:
    settings = Settings()
    db = Database(settings.db_path)
    await db.connect()
    try:
        loader = VocabularyLoader(tsv_path)
        words = loader.to_insert_dicts()
        repo = VocabularyRepository(db)
        inserted = await repo.insert_words(words)
        logger.info("Seeded %d vocabulary entries from %s", inserted, tsv_path)
        return inserted
    finally:
        await db.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(seed_vocabulary())


if __name__ == "__main__":
    main()

