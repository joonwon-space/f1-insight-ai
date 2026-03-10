"""JSON structured logging configuration."""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for structured log ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_entry.update(record.extra)  # type: ignore[arg-type]

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(json_logs: bool = True, level: int = logging.INFO) -> None:
    """Configure root logger with JSON or plain text output.

    Args:
        json_logs: If True, emit JSON log lines. If False, use human-readable format.
        level: Logging level (default INFO).
    """
    handler = logging.StreamHandler(sys.stdout)

    if json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for name in ("uvicorn.access", "watchfiles", "httpx", "httpcore", "elasticsearch"):
        logging.getLogger(name).setLevel(logging.WARNING)
