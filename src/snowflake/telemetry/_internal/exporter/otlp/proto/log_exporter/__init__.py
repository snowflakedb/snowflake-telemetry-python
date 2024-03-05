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

from opentelemetry.proto.logs.v1.logs_pb2 import LogsData
from opentelemetry.sdk import resources
from opentelemetry.sdk._logs import export
from opentelemetry.sdk import _logs
from opentelemetry.util import types
from snowflake.telemetry._internal.encoder.otlp.proto.common.log_encoder import (
    _encode_logs,
)


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
            resource_logs=_encode_logs(batch).resource_logs # pylint: disable=no-member
        ).SerializeToString()

    def shutdown(self):
        pass


class SnowflakeLoggingHandler(_logs.LoggingHandler):
    """
    A subclass of OpenTelemetry's LoggingHandler that preserves attributes
    discarded by the original implementation.
    """

    _FILEPATH_ATTRIBUTE = "code.filepath"
    _FUNCTION_NAME_ATTRIBUTE = "code.function"
    LOGGER_NAME_TEMP_ATTRIBUTE = "__snow.logging.temp.logger_name"

    def __init__(
            self,
            log_writer: LogWriter,
        ):
        provider = _SnowflakeTelemetryLogEmitterProvider()
        _logs.set_log_emitter_provider(provider)
        exporter = _ProtoLogExporter(log_writer)
        provider.add_log_processor(export.SimpleLogProcessor(exporter))
        super().__init__()

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

        # Adding attributes that were discarded by the base class's
        # _get_attributes() method
        # TODO (SNOW-1210317) Remove these when upgrading to opentelemetry-python 1.23
        attributes[SnowflakeLoggingHandler._FILEPATH_ATTRIBUTE] = record.pathname
        attributes[SnowflakeLoggingHandler._FUNCTION_NAME_ATTRIBUTE] = record.funcName

        # Temporarily storing logger's name in record's attributes.
        # This attribute will be removed by the emitter.
        #
        # TODO(SNOW-1210317): Upgrade to OpenTelemetry 1.20.0 or later
        # and use OpenTelemetry's LoggerProvider.
        attributes[SnowflakeLoggingHandler.LOGGER_NAME_TEMP_ATTRIBUTE] = record.name
        return attributes

    def _translate(self, record: logging.LogRecord) -> _logs.LogRecord:
        otel_record = super()._translate(record)
        otel_record.severity_text = SnowflakeLoggingHandler._get_snowflake_log_level_name(
            record.levelname
        )
        return otel_record


class _SnowflakeTelemetryLogEmitter(_logs.LogEmitter):
    """
    A log emitter which creates an InstrumentationScope for each logger name it
    encounters.
    """

    def __init__(
            self,
            resource: resources.Resource,
            multi_log_processor: typing.Union[
                _logs.SynchronousMultiLogProcessor, _logs.ConcurrentMultiLogProcessor
            ],
            instrumentation_scope: otel_instrumentation.InstrumentationScope,
    ):
        super().__init__(resource, multi_log_processor, instrumentation_scope)
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
        #  1. LogEmitter.emit takes a LogRecord, not LogData.
        #  2. It would emit a log record with the default instrumentation scope,
        #     not with the scope we want.
        log_data = _logs.LogData(record, current_scope)
        self._multi_log_processor.emit(log_data)


class _SnowflakeTelemetryLogEmitterProvider(_logs.LogEmitterProvider):
    """
    A log emitter provider that creates SnowflakeTelemetryLogEmitters
    """

    def get_log_emitter(
            self,
            instrumenting_module_name: str,
            instrumenting_module_version: str = "",
    ) -> _logs.LogEmitter:
        return _SnowflakeTelemetryLogEmitter(
            self._resource,
            self._multi_log_processor,
            otel_instrumentation.InstrumentationScope(
                instrumenting_module_name, instrumenting_module_version
            ),
        )


__all__ = [
    "LogWriter",
    "SnowflakeLoggingHandler",
]
