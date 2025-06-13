#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import json
import logging
import traceback

# skip natural LogRecord attributes
# http://docs.python.org/library/logging.html#logrecord-attributes
_RESERVED_ATTRS = frozenset(
    (
        "asctime",
        "args",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "message",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
        # Params that Snowflake will populate and don't want users of this API to overwrite.
        "code.lineno",
        "code.function",
        "code.filepath",
        "exception.type",
        "exception.message",
        "exception.stacktrace",
    )
)

_PY_LOG_LEVELS = frozenset(
    (
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG"
    )
)


class SnowflakeLogFormatter(logging.Formatter):
    """
    A formatter to emit logs in JSON format so that they can be parsed by Snowflake.
    """

    @staticmethod
    def get_severity_text(py_level_name):
        """
        Maps from Python logging level to OpenTelemetry's Severity Text.
        """
        level = py_level_name.upper()
        if level not in _PY_LOG_LEVELS:
            return "TRACE"
        if level == "WARNING":
            return "WARN"
        if level == "CRITICAL":
            return "FATAL"
        return level

    def format(self, record: logging.LogRecord) -> str:
        log_items = {
            "body": record.getMessage(),
            "severity_text": self.get_severity_text(record.levelname),
            "code.lineno": record.lineno,
            "code.function": record.funcName,
            "code.filepath": record.pathname
        }

        if record.exc_info is not None:
            exctype, value, tb = record.exc_info
            if exctype is not None:
                log_items["exception.type"] = exctype.__name__
            if value is not None and value.args:
                log_items["exception.message"] = value.args[0]
            if tb is not None:
                log_items["exception.stacktrace"] = "".join(traceback.format_exception(*record.exc_info))
            # Remove traceback to avoid emitting logs in incorrect format
            record.exc_info = None

        for attr, value in record.__dict__.items():
            if attr in _RESERVED_ATTRS:
                continue
            log_items[attr] = value

        return json.dumps(log_items)


__all__ = [
    "SnowflakeLogFormatter",
]
