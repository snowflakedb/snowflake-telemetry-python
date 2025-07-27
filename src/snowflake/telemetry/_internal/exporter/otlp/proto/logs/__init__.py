#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module allows the user to write logs serialized as protobuf messages to
the preferred location by implementing the write_logs() abstract method. The
only classes that should be accessed outside of this module are:

- LogWriter
- SnowflakeLoggingHandler

Please see the class documentation for those classes to learn more.
"""

import abc
import logging
import typing

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._log_encoder import (
    encode_logs,
)
from snowflake.telemetry._internal.opentelemetry.proto.logs.v1.logs_marshaler import LogsData
from snowflake.telemetry.logs import SnowflakeLogFormatter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import export
from opentelemetry.sdk import _logs
from opentelemetry.util import types


# pylint: disable=too-few-public-methods
class LogWriter(abc.ABC):
    """
    LogWriter abstract base class with one abstract method that must be
    implemented by the user.
    """
    @abc.abstractmethod
    def write_logs(self, serialized_logs: bytes) -> None:
        """
        Implement this method to write the serialized protobuf message to your
        preferred location. For an example implementation, see
        InMemoryLogWriter in the tests folder.
        """


class _ProtoLogExporter(export.LogExporter):
    """
    _ProtoLogExporter is an internal implementing class that should not be used
    or accessed outside this module.
    """

    def __init__(self, log_writer: LogWriter):
        super().__init__()
        self.log_writer = log_writer

    def export(self, batch: typing.Sequence[_logs.LogData]) -> export.LogExportResult:
        try:
            self.log_writer.write_logs(
                _ProtoLogExporter._serialize_logs_data(batch)
            )
            return export.LogExportResult.SUCCESS
        except Exception:
            return export.LogExportResult.FAILURE

    @staticmethod
    def _serialize_logs_data(batch: typing.Sequence[_logs.LogData]) -> bytes:
        # pylint gets confused by protobuf-generated code, that's why we must
        # disable the no-member check below.
        return LogsData(
            resource_logs=encode_logs(batch).resource_logs # pylint: disable=no-member
        ).SerializeToString()

    def shutdown(self):
        pass


class SnowflakeLoggingHandler(_logs.LoggingHandler):
    """
    A subclass of OpenTelemetry's LoggingHandler that preserves attributes
    discarded by the original implementation.
    """

    CODE_FILEPATH: typing.Final = "code.filepath"
    CODE_FILE_PATH: typing.Final = "code.file.path"
    CODE_FUNCTION: typing.Final = "code.function"
    CODE_FUNCTION_NAME: typing.Final = "code.function.name"
    CODE_LINENO: typing.Final = "code.lineno"
    CODE_LINE_NUMBER: typing.Final = "code.line.number"

    def __init__(
            self,
            log_writer: LogWriter,
        ):
        exporter = _ProtoLogExporter(log_writer)
        processor = export.SimpleLogRecordProcessor(exporter)
        provider = _logs.LoggerProvider(
            resource=Resource.get_empty(),
            multi_log_record_processor=processor
        )
        super().__init__(logger_provider=provider)

    @staticmethod
    def _get_attributes(record: logging.LogRecord) -> types.Attributes:
        attributes = _logs.LoggingHandler._get_attributes(record) # pylint: disable=protected-access

        # Preserving old naming conventions for code attributes that were changed as part of
        # https://github.com/open-telemetry/opentelemetry-python/commit/1b1e8d80c764ad3aa76abfb56a7002ddea11fdb5 in
        # order to avoid a behavior change for Snowflake customers.
        if SnowflakeLoggingHandler.CODE_FILE_PATH in attributes:
            attributes[SnowflakeLoggingHandler.CODE_FILEPATH] = attributes.pop(SnowflakeLoggingHandler.CODE_FILE_PATH)
        if SnowflakeLoggingHandler.CODE_FUNCTION_NAME in attributes:
            attributes[SnowflakeLoggingHandler.CODE_FUNCTION] = attributes.pop(
                SnowflakeLoggingHandler.CODE_FUNCTION_NAME)
        if SnowflakeLoggingHandler.CODE_LINE_NUMBER in attributes:
            attributes[SnowflakeLoggingHandler.CODE_LINENO] = attributes.pop(SnowflakeLoggingHandler.CODE_LINE_NUMBER)

        return attributes

    def _translate(self, record: logging.LogRecord) -> _logs.LogRecord:
        otel_record = super()._translate(record)
        otel_record.severity_text = SnowflakeLogFormatter.get_severity_text(record.levelname)
        return otel_record


__all__ = [
    "LogWriter",
    "SnowflakeLoggingHandler",
]
