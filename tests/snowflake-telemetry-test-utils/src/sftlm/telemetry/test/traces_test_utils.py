#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import typing

from opentelemetry.proto.trace.v1.trace_pb2 import (
    TracesData,
)
from snowflake.telemetry._internal.exporter.otlp.proto.traces import (
    SpanWriter,
)


class InMemorySpanWriter(SpanWriter):
    """Implementation of :class:`.SpanWriter` that stores protobufs in memory.

    This class is intended for testing purposes. It stores the deserialized
    protobuf messages in a list in memory that can be retrieved using the
    :func:`.get_finished_protos` method.
    """

    def __init__(self):
        self._protos = []

    def write_span(self, serialized_span: bytes) -> None:
        message = TracesData()
        message.ParseFromString(serialized_span)
        self._protos.append(message)

    def get_finished_protos(self) -> typing.Tuple[TracesData, ...]:
        return tuple(self._protos)

    def clear(self):
        self._protos.clear()
