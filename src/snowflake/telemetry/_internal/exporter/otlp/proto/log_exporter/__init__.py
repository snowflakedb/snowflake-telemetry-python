#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import abc
import enum
import logging
import logging.config
import threading
import typing
import opentelemetry.sdk.util.instrumentation as otel_instrumentation

from opentelemetry.sdk import resources
from opentelemetry.sdk._logs import export
from opentelemetry.sdk import _logs
from opentelemetry.util import types
from snowflake.telemetry._internal.encoder.otlp.proto.common.log_encoder import (
    serialize_logs_data
)

LOGGER_NAME_TEMP_ATTRIBUTE = "__snow.logging.temp.logger_name"
FILEPATH_ATTRIBUTE = "code.filepath"
FUNCTION_NAME_ATTRIBUTE = "code.function"


class LogWriterResult(enum.Enum):
    SUCCESS = 0
    FAILURE = 1


# LogWriter abstract class with one abstract method that can be overwritten:
class LogWriter(abc.ABC):

    @abc.abstractmethod
    def write_logs(self, serialized_logs: bytes) -> LogWriterResult:
        """quick"""


class _ProtoLogExporter(export.LogExporter):

    def __init__(self, log_writer: LogWriter):
        self.log_writer = log_writer

    def export(self, batch: typing.Sequence[_logs.LogData]):
        result = self.log_writer.write_logs(serialize_logs_data(batch))
        if result == LogWriterResult.FAILURE:
            return export.LogExportResult.FAILURE
        return export.LogExportResult.SUCCESS


    def shutdown(self):
        pass


class SnowflakeLoggingHandler(_logs.LoggingHandler):
    """A subclass of OpenTelemetry's LoggingHandler that preserves attributes discarded by the original implementation."""

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
    def _getSnowflakeLogLevelName(pyLevelName):
        """Adapted from the getSnowflakeLogLevelName in XP's logger.py"""
        level = pyLevelName.upper()
        if level == "WARNING":
            return "WARN"
        elif level == "CRITICAL":
            return "FATAL"
        elif level == "NOTSET":
            return "TRACE"
        else:
            return level

    def _get_attributes(self, record: logging.LogRecord) -> types.Attributes:
        attributes = super(SnowflakeLoggingHandler, self)._get_attributes(record)

        # Adding attributes that were discarded by the base class
        attributes[FILEPATH_ATTRIBUTE] = record.pathname
        attributes[FUNCTION_NAME_ATTRIBUTE] = record.funcName

        # Temporarily storing logger's name in record's attributes.
        # This attribute will be removed by the emitter.
        #
        # TODO(SNOW-975220): Upgrade to OpenTelemetry 1.20.0 or later
        # and use OpenTelemetry's LoggerProvider.
        attributes[LOGGER_NAME_TEMP_ATTRIBUTE] = record.name
        return attributes

    def _translate(self, record: logging.LogRecord) -> _logs.LogRecord:
        otel_record = super(SnowflakeLoggingHandler, self)._translate(record)
        otel_record.severity_text = SnowflakeLoggingHandler._getSnowflakeLogLevelName(record.levelname)
        return otel_record


class _SnowflakeTelemetryLogEmitter(_logs.LogEmitter):
    """A log emitter which creates an InstrumentationScope for each logger name it encounters."""

    def __init__(
            self,
            resource: resources.Resource,
            multi_log_processor: typing.Union[
                _logs.SynchronousMultiLogProcessor, _logs.ConcurrentMultiLogProcessor
            ],
            instrumentation_scope: otel_instrumentation.InstrumentationScope,
    ):
        super(_SnowflakeTelemetryLogEmitter, self).__init__(resource, multi_log_processor, instrumentation_scope)
        self._lock = threading.Lock()
        self.cached_scopes = {}

    def emit(self, record: _logs.LogRecord):
        if LOGGER_NAME_TEMP_ATTRIBUTE not in record.attributes:
            # The record doesn't contain our custom attribute with a logger name,
            # so we can call the superclass's `emit` method. It will emit a log
            # record with the default instrumentation scope.
            super(_SnowflakeTelemetryLogEmitter, self).emit(record)
            return

        # Creating an InstrumentationScope for each logger name,
        # and caching those scopes.
        logger_name = record.attributes[LOGGER_NAME_TEMP_ATTRIBUTE]
        del record.attributes[LOGGER_NAME_TEMP_ATTRIBUTE]
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

        # Remembering the fact that we emitted a log record.
        global _log_records_emitted
        _log_records_emitted = True


class _SnowflakeTelemetryLogEmitterProvider(_logs.LogEmitterProvider):
    """A log emitter provider that creates SnowflakeTelemetryLogEmitters"""

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
    "LogWriterResult",
    "SnowflakeLoggingHandler",
]
