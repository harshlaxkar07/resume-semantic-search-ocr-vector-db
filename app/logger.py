import sys
from pathlib import Path

from loguru import logger

from app.config import settings





log_directory = Path(settings.log_directory)
log_directory.mkdir(parents=True, exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    level=settings.log_level,
    colorize=True,
)

logger.add(
    log_directory / "application.log",
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
)

__all__ = ["logger"]