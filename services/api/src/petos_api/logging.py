import logging
from petos_api.core.config import settings


def setup_logging() -> None:
    level = logging.getLevelName(settings.log_level.upper())
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
