#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import abc
import typing

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExportResult,
    SpanExporter,
)
from snowflake.telemetry._internal.encoder.otlp.proto.common.trace_encoder import (
    serialize_traces_data,
)


# SpanWriter abstract class with one abstract method that can be overwritten:
class SpanWriter(abc.ABC):

    @abc.abstractmethod
    def write_span(self, serialized_spans: bytes) -> SpanExportResult:
        """quick"""


class LocalSpanExporter(SpanExporter):
    def __init__(self, span_writer: SpanWriter):
        self.span_writer = span_writer
    
    def export(
        self, spans: typing.Sequence[ReadableSpan]
    ) -> "SpanExportResult":
        return self.span_writer.write_span(serialize_traces_data(spans))

    def shutdown(self) -> None:
        pass
