#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module allows the user to write traces serialized as protobuf messages to
the preferred location by implementing the write_span() abstract method. The
only classes that should be accessed outside of this module are:

- SpanWriter
- ProtoSpanExporter

Please see the class documentation for those classes to learn more.
"""

import abc
import typing

from snowflake.telemetry.opentelemetry.exporter.otlp.proto.common.trace_encoder import (
    encode_spans,
)
from snowflake.telemetry.opentelemetry.proto.trace.v1.trace import TracesData
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExportResult,
    SpanExporter,
)


# pylint: disable=too-few-public-methods
class SpanWriter(abc.ABC):
    """
    SpanWriter abstract base class with one abstract method that must be
    implemented by the user.
    """
    @abc.abstractmethod
    def write_span(self, serialized_spans: bytes) -> None:
        """
        Implement this method to write the serialized protobuf message to your
        preferred location. For an example implementation, see
        InMemorySpanWriter in the tests folder.
        """


class ProtoSpanExporter(SpanExporter):
    """
    Implementation of the SpanExporter interface for exporting spans.

    This implementation writes serialized
    opentelemetry.proto.trace.v1.trace_pb2.TracesData protobuf messages
    according to the implementation you provide to the SpanWriter abstract base
    class above.
    """
    def __init__(self, span_writer: SpanWriter):
        super().__init__()
        self.span_writer = span_writer

    def export(
        self, spans: typing.Sequence[ReadableSpan]
    ) -> "SpanExportResult":
        try:
            self.span_writer.write_span(
                ProtoSpanExporter._serialize_traces_data(spans)
            )
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    @staticmethod
    def _serialize_traces_data(
        sdk_spans: typing.Sequence[ReadableSpan],
    ) -> bytes:
        # pylint gets confused by protobuf-generated code, that's why we must
        # disable the no-member check below.
        return bytes(TracesData(resource_spans=encode_spans(sdk_spans).resource_spans))

    def shutdown(self) -> None:
        pass


__all__ = [
    "SpanWriter",
    "ProtoSpanExporter",
]
