#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import inspect
import logging
import typing
import unittest

from opentelemetry.proto.logs.v1.logs_pb2 import (
    LogsData,
    SEVERITY_NUMBER_WARN,
    SEVERITY_NUMBER_ERROR,
    SEVERITY_NUMBER_FATAL,
)
from snowflake.telemetry._internal.exporter.otlp.proto.log_exporter import (
    LogWriter,
    SnowflakeLoggingHandler,
)


class InMemoryLogWriter(LogWriter):
    """Implementation of :class:`.LogWriter` that stores protobufs in memory.

    This class is intended for testing purposes. It stores the deserialized
    protobuf messages in a list in memory that can be retrieved using the
    :func:`.get_finished_protos` method.
    """

    def __init__(self):
        self._protos = []

    def write_logs(self, serialized_logs: bytes) -> None:
        message = LogsData()
        message.ParseFromString(serialized_logs)
        self._protos.append(message)

    def get_finished_protos(self) -> typing.Tuple[LogsData, ...]:
        return tuple(self._protos)

    def clear(self):
        self._protos.clear()


class TestSnowflakeLoggingHandler(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.log_writer = InMemoryLogWriter() # Replaced with SnowflakeLogWriter in XP
        self.logger = logging.getLogger()
        self.logger.addHandler(SnowflakeLoggingHandler(self.log_writer))
        self.this_file_name = inspect.currentframe().f_code.co_filename

    def test_snowflake_logging_handler_default_level_warn(self):
        self.log_writer.clear()
        # NOTSET should map to TRACE and not be emitted
        self.logger.log(logging.NOTSET, "nothing is wrong")
        self.logger.debug("nothing is wrong")
        self.logger.info("nothing is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        # Default log level for python is warn, so there should be no protobuf
        # for the logger.info call
        self.assertEqual(len(finished_protos), 0)

    def test_snowflake_logging_handler_warning_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.warning("warning, something is wrong")
        self.logger.warn("warn, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 2)
        warning_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            warning_log_record,
            "warning, something is wrong",
            "WARN",
            SEVERITY_NUMBER_WARN,
            this_method_name
        )
        warn_log_record = finished_protos[1].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            warn_log_record,
            "warn, something is wrong",
            "WARN",
            SEVERITY_NUMBER_WARN,
            this_method_name
        )

    def test_snowflake_logging_handler_error_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.error("error, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        error_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            error_log_record,
            "error, something is wrong",
            "ERROR",
            SEVERITY_NUMBER_ERROR,
            this_method_name
        )

    def test_snowflake_logging_handler_critical_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.critical("critical, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        fatal_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            fatal_log_record,
            "critical, something is wrong",
            "FATAL",
            SEVERITY_NUMBER_FATAL,
            this_method_name
        )

    def _log_record_check_helper(
            self,
            log_record,
            expected_body: str,
            expected_severity_text: str,
            expected_severity_number: int,
            expected_method_name: str):
        self.assertEqual(log_record.body.string_value, expected_body)
        self.assertEqual(log_record.severity_text, expected_severity_text)
        self.assertEqual(
            log_record.severity_number, expected_severity_number
        )
        self.assertEqual(
            self._get_attribute_string_value(log_record.attributes, 'code.filepath'),
            self.this_file_name
        )
        self.assertEqual(
            self._get_attribute_string_value(log_record.attributes, 'code.function'),
            expected_method_name
        )

    def _get_attribute_string_value(self, attributes, key: str) -> str:
        for attribute in attributes:
            if attribute.key == key:
                return attribute.value.string_value
