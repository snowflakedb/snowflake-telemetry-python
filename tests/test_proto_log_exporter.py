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
    LogWriterResult,
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

    def write_logs(self, serialized_logs: bytes) -> LogWriterResult:
        message = LogsData()
        message.ParseFromString(serialized_logs)
        self._protos.append(message)
        return LogWriterResult.SUCCESS

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

    def test_snowflake_logging_handler_info_level(self):
        self.log_writer.clear()
        self.logger.info("nothing is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        # Default log level for python is warn, so there should be no protobuf
        # for the logger.info call
        self.assertEqual(len(finished_protos), 0)

    def test_snowflake_logging_handler_warning_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.warning("warning, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        warn_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self.assertEqual(warn_log_record.body.string_value, "warning, something is wrong")
        self.assertEqual(warn_log_record.severity_text, "WARN")
        self.assertEqual(
            warn_log_record.severity_number, SEVERITY_NUMBER_WARN
        )
        self.assertEqual(
            self._get_attribute_string_value(warn_log_record.attributes, 'code.filepath'),
            self.this_file_name
        )
        self.assertEqual(
            self._get_attribute_string_value(warn_log_record.attributes, 'code.function'),
            this_method_name
        )

    def test_snowflake_logging_handler_error_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.error("error, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        error_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self.assertEqual(error_log_record.body.string_value, "error, something is wrong")
        self.assertEqual(error_log_record.severity_text, "ERROR")
        self.assertEqual(
            error_log_record.severity_number, SEVERITY_NUMBER_ERROR
        )
        self.assertEqual(
            self._get_attribute_string_value(error_log_record.attributes, 'code.filepath'),
            self.this_file_name
        )
        self.assertEqual(
            self._get_attribute_string_value(error_log_record.attributes, 'code.function'),
            this_method_name
        )

    def test_snowflake_logging_handler_critical_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.logger.critical("critical, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        fatal_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self.assertEqual(fatal_log_record.body.string_value, "critical, something is wrong")
        self.assertEqual(fatal_log_record.severity_text, "FATAL")
        self.assertEqual(
            fatal_log_record.severity_number, SEVERITY_NUMBER_FATAL
        )
        self.assertEqual(
            self._get_attribute_string_value(fatal_log_record.attributes, 'code.filepath'),
            self.this_file_name
        )
        self.assertEqual(
            self._get_attribute_string_value(fatal_log_record.attributes, 'code.function'),
            this_method_name
        )

    def _get_attribute_string_value(self, attributes, key: str) -> str:
        for attribute in attributes:
            if attribute.key == key:
                return attribute.value.string_value
