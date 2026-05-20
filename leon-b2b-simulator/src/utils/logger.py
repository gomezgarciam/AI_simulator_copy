import json
import logging
import sys
from datetime import datetime

from src.config.settings import settings


class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format for Google Cloud Logging.
    """

    def format(self, record):
        log_record = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "project_id": settings.GOOGLE_CLOUD_PROJECT,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        # In local dev, we might want readable logs, but for Cloud Run, JSON is king.
        # We'll stick to JSON for consistency.
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


# Global simulator logger
logger = setup_logger("bdr_simulator")
