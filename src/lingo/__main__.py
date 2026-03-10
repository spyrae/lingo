import asyncio
import logging

from lingo.bot.main import run_bot
from lingo.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    logger.info("lingo starting...")
    logger.info("Allowed users: %s", settings.allowed_user_ids or "all")
    await run_bot(settings)


if __name__ == "__main__":
    asyncio.run(main())

