# ESTANDAR
import logging
from typing import Optional

from rich.logging import RichHandler
from .progress import console

# Global configuration
_log_level: str = "INFO"
_is_configured: bool = False


def setup_logging(level: str = "INFO") -> None:
    """
    Configures the global logging for the project using Rich handler.

    Args:
         Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    Returns: None
    """
    global _log_level, _is_configured

    _log_level = level.upper()
    _is_configured = True

    # Remove all existing handlers from root logger
    root = logging.getLogger()
    root.handlers.clear()

    # Configure the root logger with RichHandler
    logging.basicConfig(
        level=getattr(logging, _log_level, logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
        force=True,)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured logger for the specified module.

    Args:
        Module name (use __name__)
        Optional level for this specific logger
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()  # Prevent duplicate handlers
    logger.propagate = True  # Let root logger handle output

    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    return logger
