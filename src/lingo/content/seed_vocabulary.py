from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from lingo.config import Settings
from lingo.content.vocabulary_loader import VocabularyLoader
from lingo.memory.database import Database
from lingo.memory.repositories.vocabulary_repository import VocabularyRepository

logger = logging.getLogger(__name__)


async def seed_vocabulary(*, tsv_path: Path | None = None) -> int:
    settings = Settings()
    vocab_dir = Path(settings.data_dir) / "vocabulary"
    db = Database(settings.db_path)
    await db.connect()
    try:
        repo = VocabularyRepository(db)
        total_inserted = 0

        if tsv_path is not None:
            loader = VocabularyLoader(tsv_path)
            words = loader.to_insert_dicts()
            inserted = await repo.insert_words(words)
            logger.info("Seeded %d vocabulary entries from %s", inserted, tsv_path)
            return inserted

        for tsv_file in sorted(vocab_dir.glob("*.tsv")):
            loader = VocabularyLoader(tsv_file)
            words = loader.to_insert_dicts()
            inserted = await repo.insert_words(words)
            logger.info("Seeded %d vocabulary entries from %s", inserted, tsv_file.name)
            total_inserted += inserted

        return total_inserted
    finally:
        await db.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(seed_vocabulary())


if __name__ == "__main__":
    main()

