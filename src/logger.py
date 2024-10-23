import logging
import os


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "log.log")

logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ])
logger = logging.getLogger("CodeReviewAI")


def log_error(message: str, exc_info: bool = True) -> None:
    """
    Logs an error message with optional exception information.

    Args:
        message (str): The error message to log.
        exc_info (bool): If True, logs exception information. Defaults to True.

    """
    logger.error(message, exc_info=exc_info)


def log_info(message: str) -> None:
    """
    Logs an informational message.

    Args:
        message (str): The informational message to log.

    """
    logger.info(message)


def log_warning(message: str) -> None:
    """
    Logs a warning message.

    Args:
        message (str): The warning message to log.

    """
    logger.warning(message)
