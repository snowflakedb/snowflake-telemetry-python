#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module is a temporary bridge from opentelemetry 1.12.0 our current
dependency, which does not have common encoder functions to the later versions
of opentelemetry, which do have common encoder functions in the
opentelemetry-exporter-otlp-proto-common package.
"""

from typing import Sequence

from opentelemetry.exporter.otlp.proto.http.trace_exporter.encoder import _ProtobufEncoder
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.sdk.trace import ReadableSpan


def _encode_spans(
    sdk_spans: Sequence[ReadableSpan],
) -> ExportTraceServiceRequest:
    # Will no longer rely on _ProtobufEncoder after we upgrade to v1.19.0 or later
    return _ProtobufEncoder.encode(sdk_spans)
