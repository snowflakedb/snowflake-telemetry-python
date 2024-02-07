#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

from typing import Sequence

from opentelemetry.exporter.otlp.proto.http.trace_exporter.encoder import _ProtobufEncoder
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
from opentelemetry.sdk.trace import ReadableSpan


def _encode_spans(
    sdk_spans: Sequence[ReadableSpan],
) -> ExportTraceServiceRequest:
    # Will no longer rely on _ProtobufEncoder after we upgrade to v1.19.0 or later
    return _ProtobufEncoder.encode(sdk_spans)

def serialize_traces_data(
    sdk_spans: Sequence[ReadableSpan],
) -> bytes:
    return TracesData(
        resource_spans=_encode_spans(sdk_spans).resource_spans
    ).SerializeToString()


__all__ = [
    "serialize_traces_data",
]
