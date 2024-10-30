# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from collections.abc import Sequence
from typing import (
    Any,
    Mapping,
    Optional,
    List,
    TypeVar,
)

from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from snowflake.telemetry._internal.opentelemetry.proto.common.v1.common import (
    InstrumentationScope as MarshalInstrumentationScope,
)
from snowflake.telemetry._internal.opentelemetry.proto.resource.v1.resource import (
    Resource as MarshalResource,
)
from snowflake.telemetry._internal.opentelemetry.proto.common.v1.common import (
    KeyValueList as MarshalKeyValueList,
    ArrayValue as MarshalArrayValue,
    KeyValue as MarshalKeyValue,
    AnyValue as MarshalAnyValue,
)
from opentelemetry.sdk.trace import Resource
from opentelemetry.util.types import Attributes

_logger = logging.getLogger(__name__)

_TypingResourceT = TypeVar("_TypingResourceT")
_ResourceDataT = TypeVar("_ResourceDataT")


def _encode_instrumentation_scope(
    instrumentation_scope: InstrumentationScope,
) -> bytes:
    if instrumentation_scope is None:
        return MarshalInstrumentationScope()
    return MarshalInstrumentationScope(
        name=instrumentation_scope.name,
        version=instrumentation_scope.version,
    )


def _encode_resource(resource: Resource) -> bytes:
    return MarshalResource(attributes=_encode_attributes(resource.attributes))


def _encode_value(value: Any) -> bytes:
    if isinstance(value, bool):
        return MarshalAnyValue(bool_value=value)
    if isinstance(value, str):
        return MarshalAnyValue(string_value=value)
    if isinstance(value, int):
        return MarshalAnyValue(int_value=value)
    if isinstance(value, float):
        return MarshalAnyValue(double_value=value)
    if isinstance(value, Sequence):
        return MarshalAnyValue(
            array_value=MarshalArrayValue(values=[_encode_value(v) for v in value])
        )
    elif isinstance(value, Mapping):
        return MarshalAnyValue(
            kvlist_value=MarshalKeyValueList(
                values=[_encode_key_value(str(k), v) for k, v in value.items()]
            )
        )
    raise Exception(f"Invalid type {type(value)} of value {value}")


def _encode_key_value(key: str, value: Any) -> bytes:
    return MarshalKeyValue(key=key, value=_encode_value(value))


def _encode_span_id(span_id: int) -> bytes:
    return span_id.to_bytes(length=8, byteorder="big", signed=False)


def _encode_trace_id(trace_id: int) -> bytes:
    return trace_id.to_bytes(length=16, byteorder="big", signed=False)


def _encode_attributes(
    attributes: Attributes,
) -> Optional[List[bytes]]:
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