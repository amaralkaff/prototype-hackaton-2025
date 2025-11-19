from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_file: str = "./logs/amara_api.log", log_level: str = "INFO"):
    """Configure application logger"""

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove default logger
    logger.remove()

    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file logger
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=log_level,
        rotation="500 MB",
        retention="10 days",
        compression="zip",
    )

    logger.info(f"Logger initialized - Level: {log_level}")

    return logger
