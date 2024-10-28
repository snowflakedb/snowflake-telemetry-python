import unittest

from dataclasses import dataclass
from typing import Any, Dict, Callable
import hypothesis
from hypothesis.strategies import composite, text, booleans, integers, floats, lists, binary, sampled_from

import hypothesis.strategies
import opentelemetry.proto.logs.v1.logs_pb2 as logs_pb2
import opentelemetry.proto.trace.v1.trace_pb2 as trace_pb2
import opentelemetry.proto.common.v1.common_pb2 as common_pb2
import opentelemetry.proto.metrics.v1.metrics_pb2 as metrics_pb2
import opentelemetry.proto.resource.v1.resource_pb2 as resource_pb2

import snowflake.telemetry._internal.opentelemetry.proto.logs.v1.logs as logs_sf
import snowflake.telemetry._internal.opentelemetry.proto.trace.v1.trace as trace_sf
import snowflake.telemetry._internal.opentelemetry.proto.common.v1.common as common_sf
import snowflake.telemetry._internal.opentelemetry.proto.metrics.v1.metrics as metrics_sf
import snowflake.telemetry._internal.opentelemetry.proto.resource.v1.resource as resource_sf

# Strategy for generating protobuf types
def pb_uint32(): return integers(min_value=0, max_value=2**32-1)
def pb_uint64(): return integers(min_value=0, max_value=2**64-1)
def pb_int32(): return integers(min_value=-2**31, max_value=2**31-1)
def pb_int64(): return integers(min_value=-2**63, max_value=2**63-1)
def pb_sint32(): return integers(min_value=-2**31, max_value=2**31-1)
def pb_sint64(): return integers(min_value=-2**63, max_value=2**63-1)
def pb_float(): return floats(allow_nan=False, allow_infinity=False, width=32)
def pb_double(): return floats(allow_nan=False, allow_infinity=False, width=64)
def pb_fixed64(): return pb_uint64()
def pb_fixed32(): return pb_uint32()
def pb_sfixed64(): return pb_int64()
def pb_sfixed32(): return pb_int32()
def pb_bool(): return booleans()
def pb_string(): return text()
def pb_bytes(): return binary()
def pb_enum(enum): return sampled_from([member.value for member in enum])

# Maps protobuf types to their serialization functions, from the protobuf and snowflake serialization libraries
@dataclass
class EncodeStrategy:
    pb2: Callable[[Any], Any]
    sf: Callable[[Any], Any]

Resource = EncodeStrategy(pb2=resource_pb2.Resource, sf=resource_sf.Resource)
InstrumentationScope = EncodeStrategy(pb2=common_pb2.InstrumentationScope, sf=common_sf.InstrumentationScope)
AnyValue = EncodeStrategy(pb2=common_pb2.AnyValue, sf=common_sf.AnyValue)
ArrayValue = EncodeStrategy(pb2=common_pb2.ArrayValue, sf=common_sf.ArrayValue)
KeyValue = EncodeStrategy(pb2=common_pb2.KeyValue, sf=common_sf.KeyValue)
KeyValueList = EncodeStrategy(pb2=common_pb2.KeyValueList, sf=common_sf.KeyValueList)
LogRecord = EncodeStrategy(pb2=logs_pb2.LogRecord, sf=logs_sf.LogRecord)
ScopeLogs = EncodeStrategy(pb2=logs_pb2.ScopeLogs, sf=logs_sf.ScopeLogs)
ResourceLogs = EncodeStrategy(pb2=logs_pb2.ResourceLogs, sf=logs_sf.ResourceLogs)
LogsData = EncodeStrategy(pb2=logs_pb2.LogsData, sf=logs_sf.LogsData)

# Package the protobuf type with its arguments for serialization
@dataclass
class EncodeWithArgs:
    kwargs: Dict[str, Any]
    cls: EncodeStrategy

# Strategies for generating opentelemetry-proto types
@composite
def instrumentation_scope(draw):
    return EncodeWithArgs({
        "name": draw(pb_string()),
        "version": draw(pb_string()),
        "attributes": draw(lists(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
    }, InstrumentationScope)

@composite
def resource(draw):
    return EncodeWithArgs({
        "attributes": draw(lists(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
    }, Resource)

@composite
def any_value(draw):
    # oneof field so only set one
    oneof = draw(integers(min_value=0, max_value=6))
    if oneof == 0:
        kwargs = {"string_value": draw(pb_string())}
    elif oneof == 1:
        kwargs = {"bool_value": draw(pb_bool())}
    elif oneof == 2:
        kwargs = {"int_value": draw(pb_int64())}
    elif oneof == 3:
        kwargs = {"double_value": draw(pb_double())}
    elif oneof == 4:
        kwargs = {"array_value": draw(array_value())}
    elif oneof == 5:
        kwargs = {"kvlist_value": draw(key_value_list())}
    elif oneof == 6:
        kwargs = {"bytes_value": draw(pb_bytes())}
    return EncodeWithArgs(kwargs, AnyValue)

@composite
def array_value(draw):
    return EncodeWithArgs({
        "values": draw(lists(any_value())),
    }, ArrayValue)

@composite
def key_value(draw):
    return EncodeWithArgs({
        "key": draw(pb_string()),
        "value": draw(any_value()),
    }, KeyValue)

@composite
def key_value_list(draw):
    return EncodeWithArgs({
        "values": draw(lists(key_value())),
    }, KeyValueList)

@composite
def log_record(draw):
    return EncodeWithArgs({
        "time_unix_nano": draw(pb_fixed64()),
        "observed_time_unix_nano": draw(pb_fixed64()),
        "severity_number": draw(pb_enum(logs_sf.SeverityNumber)),
        "severity_text": draw(pb_string()),
        "body": draw(any_value()),
        "attributes": draw(lists(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
        "flags": draw(pb_fixed32()),
        "span_id": draw(pb_bytes()),
        "trace_id": draw(pb_bytes()),
    }, LogRecord)

@composite
def scope_logs(draw):
    return EncodeWithArgs({
        "scope": draw(instrumentation_scope()),
        "log_records": draw(lists(log_record())),
        "schema_url": draw(pb_string()),
    }, ScopeLogs)

@composite
def resource_logs(draw):
    return EncodeWithArgs({
        "resource": draw(resource()),
        "scope_logs": draw(lists(scope_logs())),
        "schema_url": draw(pb_string()),
    }, ResourceLogs)

@composite
def logs_data(draw):
    return EncodeWithArgs({
        "resource_logs": draw(lists(resource_logs())),
    }, LogsData)

# Helper function to recursively encode protobuf types using the generated args 
# and the given serialization strategy
def encode_recurse(obj: EncodeWithArgs, strategy: str) -> Any:
    kwargs = {}
    for key, value in obj.kwargs.items():
        if isinstance(value, EncodeWithArgs):
            kwargs[key] = encode_recurse(value, strategy)
        elif isinstance(value, list) and value and isinstance(value[0], EncodeWithArgs):
            kwargs[key] = [encode_recurse(v, strategy) for v in value]
        else:
            kwargs[key] = value
    if strategy == "pb2":
        return obj.cls.pb2(**kwargs)
    elif strategy == "sf":
        return obj.cls.sf(**kwargs)

class TestProtoSerialization(unittest.TestCase):
    @hypothesis.settings(
        suppress_health_check=[
            hypothesis.HealthCheck.too_slow,
        ],
    )
    @hypothesis.given(logs_data())
    def test_log_data(self, logs_data):
        self.assertEqual(
            encode_recurse(logs_data, "pb2").SerializeToString(),
            bytes(encode_recurse(logs_data, "sf"))
        )
