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
import logging.config
import threading
import typing
import opentelemetry.sdk.util.instrumentation as otel_instrumentation
import opentelemetry.sdk._logs._internal as _logs_internal

from opentelemetry.exporter.otlp.proto.common._log_encoder import (
    encode_logs,
)
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData
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

    LOGGER_NAME_TEMP_ATTRIBUTE = "__snow.logging.temp.logger_name"

    def __init__(
            self,
            log_writer: LogWriter,
        ):
        exporter = _ProtoLogExporter(log_writer)
        provider = _SnowflakeTelemetryLoggerProvider()
        provider.add_log_record_processor(
            export.SimpleLogRecordProcessor(exporter)
        )
        super().__init__(logger_provider=provider)

    @staticmethod
    def _get_snowflake_log_level_name(py_level_name):
        """
        Adapted from the getSnowflakeLogLevelName method in XP's logger.py
        """
        level = py_level_name.upper()
        if level == "WARNING":
            return "WARN"
        if level == "CRITICAL":
            return "FATAL"
        if level == "NOTSET":
            return "TRACE"
        return level

    @staticmethod
    def _get_attributes(record: logging.LogRecord) -> types.Attributes:
        attributes = _logs.LoggingHandler._get_attributes(record) # pylint: disable=protected-access

        # Temporarily storing logger's name in record's attributes.
        # This attribute will be removed by the logger.
        #
        # TODO (SNOW-1235374): opentelemetry-python issue #2485: Record logger
        # name as the instrumentation scope name
        attributes[SnowflakeLoggingHandler.LOGGER_NAME_TEMP_ATTRIBUTE] = record.name
        return attributes

    def _translate(self, record: logging.LogRecord) -> _logs.LogRecord:
        otel_record = super()._translate(record)
        otel_record.severity_text = SnowflakeLoggingHandler._get_snowflake_log_level_name(
            record.levelname
        )
        return otel_record


class _SnowflakeTelemetryLogger(_logs.Logger):
    """
    An Open Telemetry Logger which creates an InstrumentationScope for each
    logger name it encounters.
    """

    def __init__(
        self,
        resource: Resource,
        multi_log_record_processor: typing.Union[
            _logs_internal.SynchronousMultiLogRecordProcessor,
            _logs_internal.ConcurrentMultiLogRecordProcessor,
        ],
        instrumentation_scope: otel_instrumentation.InstrumentationScope,
    ):
        super().__init__(resource, multi_log_record_processor, instrumentation_scope)
        self._lock = threading.Lock()
        self.cached_scopes = {}

    def emit(self, record: _logs.LogRecord):
        if SnowflakeLoggingHandler.LOGGER_NAME_TEMP_ATTRIBUTE not in record.attributes:
            # The record doesn't contain our custom attribute with a logger name,
            # so we can call the superclass's `emit` method. It will emit a log
            # record with the default instrumentation scope.
            super().emit(record)
            return

        # Creating an InstrumentationScope for each logger name,
        # and caching those scopes.
        logger_name = record.attributes[SnowflakeLoggingHandler.LOGGER_NAME_TEMP_ATTRIBUTE]
        del record.attributes[SnowflakeLoggingHandler.LOGGER_NAME_TEMP_ATTRIBUTE]
        with self._lock:
            if logger_name in self.cached_scopes:
                current_scope = self.cached_scopes[logger_name]
            else:
                current_scope = otel_instrumentation.InstrumentationScope(logger_name)
                self.cached_scopes[logger_name] = current_scope

        # Emitting a record with a scope that corresponds to the logger
        # that logged it. NOT calling the superclass here for two reasons:
        #  1. Logger.emit takes a LogRecord, not LogData.
        #  2. It would emit a log record with the default instrumentation scope,
        #     not with the scope we want.
        log_data = _logs.LogData(record, current_scope)
        self._multi_log_record_processor.emit(log_data)


class _SnowflakeTelemetryLoggerProvider(_logs.LoggerProvider):
    """
    A LoggerProvider that creates SnowflakeTelemetryLoggers
    """

    def get_logger(
            self, name: str,
            version: types.Optional[str] = None,
            schema_url: types.Optional[str] = None,
            attributes: types.Optional[types.Attributes] = None,
    ) -> _logs.Logger:
        return _SnowflakeTelemetryLogger(
            Resource.get_empty(),
            self._multi_log_record_processor,
            otel_instrumentation.InstrumentationScope(
                name,
                version,
                schema_url,
            ),
        )


__all__ = [
    "LogWriter",
    "SnowflakeLoggingHandler",
]
