# -*- coding: utf-8 -*-
"""Logging configuration for Excel API"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging"""

    class JSONFormatter(logging.Formatter):
        """Format logs as JSON for better observability"""

        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)

            if hasattr(record, "extra_data"):
                log_data.update(record.extra_data)

            return json.dumps(log_data)

    # Get or create root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


# Initialize on import
logger = setup_logging()
