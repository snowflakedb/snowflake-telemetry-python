#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import inspect
import logging
import unittest

from opentelemetry.proto.logs.v1.logs_pb2 import (
    SEVERITY_NUMBER_WARN,
    SEVERITY_NUMBER_ERROR,
    SEVERITY_NUMBER_FATAL,
)
from snowflake.telemetry._internal.exporter.otlp.proto.logs import (
    SnowflakeLoggingHandler,
)
from snowflake.telemetry.test.logs_test_utils import InMemoryLogWriter


class TestSnowflakeLoggingHandler(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.log_writer = InMemoryLogWriter() # Replaced with SnowflakeLogWriter in XP
        self.root_logger = logging.getLogger()
        self.root_logger.addHandler(SnowflakeLoggingHandler(self.log_writer))
        self.this_file_name = inspect.currentframe().f_code.co_filename

    def test_snowflake_logging_handler_default_level_warn(self):
        self.log_writer.clear()
        # NOTSET should map to TRACE and not be emitted
        self.root_logger.log(logging.NOTSET, "nothing is wrong")
        self.root_logger.debug("nothing is wrong")
        self.root_logger.info("nothing is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        # Default log level for python is warn, so there should be no protobuf
        # for the logger.info call
        self.assertEqual(len(finished_protos), 0)

    def test_snowflake_logging_handler_warning_level(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.root_logger.warning("warning, something is wrong")
        self.root_logger.warn("warn, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 2)
        self.assertEqual(len(finished_protos[0].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[0].resource_logs[0].scope_logs[0].scope.name, "root")
        warning_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            warning_log_record,
            "warning, something is wrong",
            "WARN",
            SEVERITY_NUMBER_WARN,
            this_method_name
        )
        self.assertEqual(len(finished_protos[1].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[1].resource_logs[0].scope_logs[0].scope.name, "root")
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
        self.root_logger.error("error, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        self.assertEqual(len(finished_protos[0].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[0].resource_logs[0].scope_logs[0].scope.name, "root")
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
        self.root_logger.critical("critical, something is wrong")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 1)
        self.assertEqual(len(finished_protos[0].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[0].resource_logs[0].scope_logs[0].scope.name, "root")
        fatal_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            fatal_log_record,
            "critical, something is wrong",
            "FATAL",
            SEVERITY_NUMBER_FATAL,
            this_method_name
        )

    def test_snowflake_logging_handler_scoped_logger(self):
        this_method_name = inspect.currentframe().f_code.co_name
        self.log_writer.clear()
        self.root_logger.critical("critical, something is wrong at root scope")
        local_logger = logging.getLogger("tests")
        local_logger.critical("critical, something is wrong at local scope")
        finished_protos = self.log_writer.get_finished_protos()
        self.assertEqual(len(finished_protos), 2)
        self.assertEqual(len(finished_protos[0].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[0].resource_logs[0].scope_logs[0].scope.name, "root")
        root_log_record = finished_protos[0].resource_logs[0].scope_logs[0].log_records[0]
        self._log_record_check_helper(
            root_log_record,
            "critical, something is wrong at root scope",
            "FATAL",
            SEVERITY_NUMBER_FATAL,
            this_method_name
        )
        local_log_record = finished_protos[1].resource_logs[0].scope_logs[0].log_records[0]
        self.assertEqual(len(finished_protos[1].resource_logs[0].resource.attributes), 0)
        self.assertEqual(finished_protos[1].resource_logs[0].scope_logs[0].scope.name, "tests")
        self._log_record_check_helper(
            local_log_record,
            "critical, something is wrong at local scope",
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
        self.assertGreaterEqual(
            self._get_attribute_int_value(log_record.attributes, 'code.lineno'),
            0
        )


    def _get_attribute_string_value(self, attributes, key: str) -> str:
        for attribute in attributes:
            if attribute.key == key:
                return attribute.value.string_value

    def _get_attribute_int_value(self, attributes, key: str) -> int:
        for attribute in attributes:
            if attribute.key == key:
                return attribute.value.int_value
