import json
import logging
import unittest
from io import StringIO

from snowflake.telemetry.logs import SnowflakeLogFormatter


class TestSnowflakeLogFormatter(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.stream = StringIO()
        self.root_logger = logging.getLogger("test")
        self.root_hdlr = logging.StreamHandler(self.stream)
        formatter = SnowflakeLogFormatter()
        self.root_hdlr.setFormatter(formatter)
        self.root_logger.addHandler(self.root_hdlr)

    def test_normal_log(self):
        """ Does the logger produce the correct output? """
        self.root_logger.warning('foo', extra={"test": 123, "code.lineno": 35})
        expected_log_message = {
            "body": "foo",
            "severity_text": "WARN",
            "code.lineno": 21,
            "code.function": "test_normal_log",
            "test": 123
        }
        actual_log_message = json.loads(self.stream.getvalue())
        actual_filepath = actual_log_message.pop("code.filepath")
        self.assertIn("snowflake-telemetry-python/tests/test_snowflake_log_formatter.py", actual_filepath)
        self.assertEqual(expected_log_message, actual_log_message)

    def test_exception_log(self):
        """ Does the logger include exception details? """
        try:
            10 / 0
        except ZeroDivisionError:
            self.root_logger.exception("\"test exception\"")

        expected_log_message = {
            "body": "\"test exception\"",
            "severity_text": "ERROR",
            "code.lineno": 39,
            "code.function": "test_exception_log",
            "exception.type": "ZeroDivisionError",
            "exception.message": "division by zero",
        }
        actual_log_message = json.loads(self.stream.getvalue(), strict=False)
        actual_log_message.pop("code.filepath")
        actual_stacktrace = actual_log_message.pop("exception.stacktrace")
        self.assertIn("line 37, in test_exception_log\n", actual_stacktrace)
        self.assertIn("ZeroDivisionError: division by zero\n", actual_stacktrace)
        self.assertEqual(expected_log_message, actual_log_message)

    def test_get_severity_text(self):
        """ Does get_severity_text work correctly? """
        self.assertEqual("INFO", SnowflakeLogFormatter.get_severity_text("info"))
        self.assertEqual("FATAL", SnowflakeLogFormatter.get_severity_text("critical"))
        self.assertEqual("WARN", SnowflakeLogFormatter.get_severity_text("warning"))
        self.assertEqual("DEBUG", SnowflakeLogFormatter.get_severity_text("debug"))
        self.assertEqual("ERROR", SnowflakeLogFormatter.get_severity_text("error"))
        self.assertEqual("TRACE", SnowflakeLogFormatter.get_severity_text("notset"))
        self.assertEqual("TRACE", SnowflakeLogFormatter.get_severity_text("random"))
