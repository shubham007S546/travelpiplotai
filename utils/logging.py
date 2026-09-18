"""Structured logging for TravelPilot AI multi-agent execution."""

import logging
import os
import sys
from typing import Optional


def setup_logger(name: str = "travelpilot", level: Optional[str] = None) -> logging.Logger:
    """Configures a standardized console logger with clear agent formatting."""
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(log_level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
