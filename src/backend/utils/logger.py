import logging
import sys
from pathlib import Path

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(log_file: str = "logs/kubeheal.log"):
    Path("logs").mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <white>{message}</white>",
        level="INFO",
    )

    logger.add(
        log_file,
        rotation="10 MB",
        retention="5 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        level="ERROR",
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

    return logger
