import logging
from typing import Any, List, Mapping, Optional, Sequence
from opentelemetry.util.types import Attributes
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import Status
from opentelemetry.proto.common.v1.common_pb2 import (
    AnyValue as PB2AnyValue,
    ArrayValue as PB2ArrayValue,
    KeyValue as PB2KeyValue,
    KeyValueList as PB2KeyValueList,
)
from opentelemetry.proto.trace.v1.trace_pb2 import (
    Status as PB2Status,
    Span as PB2SPan,
)


_logger = logging.getLogger(__name__)


def _encode_span_id(span_id: int) -> bytes:
    return span_id.to_bytes(length=8, byteorder="big", signed=False)


def _encode_trace_id(trace_id: int) -> bytes:
    return trace_id.to_bytes(length=16, byteorder="big", signed=False)


def _encode_key_value(key: str, value: Any) -> PB2KeyValue:
    return PB2KeyValue(key=key, value=_encode_value(value))


def _encode_attributes(
    attributes: Attributes,
) -> Optional[List[PB2KeyValue]]:
    if attributes:
        pb2_attributes = []
        for key, value in attributes.items():
            # pylint: disable=broad-exception-caught
            try:
                pb2_attributes.append(_encode_key_value(key, value))
            except Exception as error:
                _logger.exception("Failed to encode key %s: %s", key, error)
    else:
        pb2_attributes = None
    return pb2_attributes


def _encode_value(value: Any) -> PB2AnyValue:
    if isinstance(value, bool):
        return PB2AnyValue(bool_value=value)
    if isinstance(value, str):
        return PB2AnyValue(string_value=value)
    if isinstance(value, int):
        return PB2AnyValue(int_value=value)
    if isinstance(value, float):
        return PB2AnyValue(double_value=value)
    if isinstance(value, Sequence):
        return PB2AnyValue(
            array_value=PB2ArrayValue(values=[_encode_value(v) for v in value])
        )
    elif isinstance(value, Mapping):
        return PB2AnyValue(
            kvlist_value=PB2KeyValueList(
                values=[_encode_key_value(str(k), v) for k, v in value.items()]
            )
        )
    raise Exception(f"Invalid type {type(value)} of value {value}")


_SPAN_KIND_MAP = {
    SpanKind.INTERNAL: PB2SPan.SpanKind.SPAN_KIND_INTERNAL,
    SpanKind.SERVER: PB2SPan.SpanKind.SPAN_KIND_SERVER,
    SpanKind.CLIENT: PB2SPan.SpanKind.SPAN_KIND_CLIENT,
    SpanKind.PRODUCER: PB2SPan.SpanKind.SPAN_KIND_PRODUCER,
    SpanKind.CONSUMER: PB2SPan.SpanKind.SPAN_KIND_CONSUMER,
}


def _encode_status(status: Status) -> Optional[PB2Status]:
    pb2_status = None
    if status is not None:
        pb2_status = PB2Status(
            code=status.status_code.value,
            message=status.description,
        )
    return pb2_status
