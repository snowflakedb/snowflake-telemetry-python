import unittest

from dataclasses import dataclass
from typing import Any, Dict, Callable
import hypothesis
from hypothesis.strategies import composite, text, booleans, integers, floats, lists, binary, sampled_from
from hypothesis.control import assume

import hypothesis.strategies
import opentelemetry.proto.logs.v1.logs_pb2 as logs_pb2
import opentelemetry.proto.trace.v1.trace_pb2 as trace_pb2
import opentelemetry.proto.common.v1.common_pb2 as common_pb2
import opentelemetry.proto.metrics.v1.metrics_pb2 as metrics_pb2
import opentelemetry.proto.resource.v1.resource_pb2 as resource_pb2

import snowflake.telemetry._internal.opentelemetry.proto.logs.v1 as logs_sf
import snowflake.telemetry._internal.opentelemetry.proto.trace.v1 as trace_sf
import snowflake.telemetry._internal.opentelemetry.proto.common.v1 as common_sf
import snowflake.telemetry._internal.opentelemetry.proto.metrics.v1 as metrics_sf
import snowflake.telemetry._internal.opentelemetry.proto.resource.v1 as resource_sf

# Strategy for generating protobuf types
def pb_uint32(): return integers(min_value=0, max_value=2**32-1)
def pb_uint64(): return integers(min_value=0, max_value=2**64-1)
def pb_int32(): return integers(min_value=-2**31, max_value=2**31-1)
def pb_int64(): return integers(min_value=-2**63, max_value=2**63-1)
def pb_sint32(): return integers(min_value=-2**31, max_value=2**31-1)
def pb_sint64(): return integers(min_value=-2**63, max_value=2**63-1)
def pb_float(): return floats(allow_nan=False, allow_infinity=False, width=32)
def pb_double(): return floats(allow_nan=False, allow_infinity=False, width=64)
def draw_pb_double(draw):
    # -0.0 is an edge case that is not handled by the snowflake serialization library
    # Protobuf serialization will serialize -0.0 as "-0.0", and omit 0.0
    # Snowflake will omit both -0.0 and 0.0
    double = draw(pb_double())
    assume(str(double) != "-0.0")
    return double
def pb_fixed64(): return pb_uint64()
def pb_fixed32(): return pb_uint32()
def pb_sfixed64(): return pb_int64()
def pb_sfixed32(): return pb_int32()
def pb_bool(): return booleans()
def pb_string(): return text(max_size=20)
def pb_bytes(): return binary(max_size=20)
def pb_enum(enum): return sampled_from([member.value for member in enum])
def pb_repeated(type): return lists(type, max_size=3) # limit the size of the repeated field to speed up testing
def pb_span_id(): return binary(min_size=8, max_size=8)
def pb_trace_id(): return binary(min_size=16, max_size=16)

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

TracesData = EncodeStrategy(pb2=trace_pb2.TracesData, sf=trace_sf.TracesData)
ScopeSpans = EncodeStrategy(pb2=trace_pb2.ScopeSpans, sf=trace_sf.ScopeSpans)
ResourceSpans = EncodeStrategy(pb2=trace_pb2.ResourceSpans, sf=trace_sf.ResourceSpans)
Span = EncodeStrategy(pb2=trace_pb2.Span, sf=trace_sf.Span)
Event = EncodeStrategy(pb2=trace_pb2.Span.Event, sf=trace_sf.Span.Event)
Link = EncodeStrategy(pb2=trace_pb2.Span.Link, sf=trace_sf.Span.Link)
Status = EncodeStrategy(pb2=trace_pb2.Status, sf=trace_sf.Status)

Metric = EncodeStrategy(pb2=metrics_pb2.Metric, sf=metrics_sf.Metric)
ScopeMetrics = EncodeStrategy(pb2=metrics_pb2.ScopeMetrics, sf=metrics_sf.ScopeMetrics)
ResourceMetrics = EncodeStrategy(pb2=metrics_pb2.ResourceMetrics, sf=metrics_sf.ResourceMetrics)
MetricsData = EncodeStrategy(pb2=metrics_pb2.MetricsData, sf=metrics_sf.MetricsData)
Gauge = EncodeStrategy(pb2=metrics_pb2.Gauge, sf=metrics_sf.Gauge)
Sum = EncodeStrategy(pb2=metrics_pb2.Sum, sf=metrics_sf.Sum)
Histogram = EncodeStrategy(pb2=metrics_pb2.Histogram, sf=metrics_sf.Histogram)
ExponentialHistogram = EncodeStrategy(pb2=metrics_pb2.ExponentialHistogram, sf=metrics_sf.ExponentialHistogram)
Summary = EncodeStrategy(pb2=metrics_pb2.Summary, sf=metrics_sf.Summary)
NumberDataPoint = EncodeStrategy(pb2=metrics_pb2.NumberDataPoint, sf=metrics_sf.NumberDataPoint)
Exemplar = EncodeStrategy(pb2=metrics_pb2.Exemplar, sf=metrics_sf.Exemplar)
HistogramDataPoint = EncodeStrategy(pb2=metrics_pb2.HistogramDataPoint, sf=metrics_sf.HistogramDataPoint)
ExponentialHistogramDataPoint = EncodeStrategy(pb2=metrics_pb2.ExponentialHistogramDataPoint, sf=metrics_sf.ExponentialHistogramDataPoint)
SummaryDataPoint = EncodeStrategy(pb2=metrics_pb2.SummaryDataPoint, sf=metrics_sf.SummaryDataPoint)
ValueAtQuantile = EncodeStrategy(pb2=metrics_pb2.SummaryDataPoint.ValueAtQuantile, sf=metrics_sf.SummaryDataPoint.ValueAtQuantile)
Buckets = EncodeStrategy(pb2=metrics_pb2.ExponentialHistogramDataPoint.Buckets, sf=metrics_sf.ExponentialHistogramDataPoint.Buckets)


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
        "attributes": draw(pb_repeated(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
    }, InstrumentationScope)

@composite
def resource(draw):
    return EncodeWithArgs({
        "attributes": draw(pb_repeated(key_value())),
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
        kwargs = {"double_value": draw_pb_double(draw)}
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
        "values": draw(pb_repeated(any_value())),
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
        "values": draw(pb_repeated(key_value())),
    }, KeyValueList)

@composite
def logs_data(draw):
    @composite
    def log_record(draw):
        return EncodeWithArgs({
            "time_unix_nano": draw(pb_fixed64()),
            "observed_time_unix_nano": draw(pb_fixed64()),
            "severity_number": draw(pb_enum(logs_sf.SeverityNumber)),
            "severity_text": draw(pb_string()),
            "body": draw(any_value()),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
            "span_id": draw(pb_span_id()),
            "trace_id": draw(pb_trace_id()),
        }, LogRecord)

    @composite
    def scope_logs(draw):
        return EncodeWithArgs({
            "scope": draw(instrumentation_scope()),
            "log_records": draw(pb_repeated(log_record())),
            "schema_url": draw(pb_string()),
        }, ScopeLogs)

    @composite
    def resource_logs(draw):
        return EncodeWithArgs({
            "resource": draw(resource()),
            "scope_logs": draw(pb_repeated(scope_logs())),
            "schema_url": draw(pb_string()),
        }, ResourceLogs)
    
    return EncodeWithArgs({
        "resource_logs": draw(pb_repeated(resource_logs())),
    }, LogsData)

@composite
def traces_data(draw):
    @composite
    def event(draw):
        return EncodeWithArgs({
            "time_unix_nano": draw(pb_fixed64()),
            "name": draw(pb_string()),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
        }, Event)
    
    @composite
    def link(draw):
        return EncodeWithArgs({
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "trace_state": draw(pb_string()),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
        }, Link)
    
    @composite
    def status(draw):
        return EncodeWithArgs({
            "code": draw(pb_enum(trace_sf.Status.StatusCode)),
            "message": draw(pb_string()),
        }, Status)
    
    @composite
    def span(draw):
        return EncodeWithArgs({
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "trace_state": draw(pb_string()),
            "parent_span_id": draw(pb_span_id()),
            "name": draw(pb_string()),
            "kind": draw(pb_enum(trace_sf.Span.SpanKind)),
            "start_time_unix_nano": draw(pb_fixed64()),
            "end_time_unix_nano": draw(pb_fixed64()),
            "attributes": draw(pb_repeated(key_value())),
            "events": draw(pb_repeated(event())),
            "links": draw(pb_repeated(link())),
            "status": draw(status()),
            "dropped_attributes_count": draw(pb_uint32()),
            "dropped_events_count": draw(pb_uint32()),
            "dropped_links_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
        }, Span)

    @composite
    def scope_spans(draw):
        return EncodeWithArgs({
            "scope": draw(instrumentation_scope()),
            "spans": draw(pb_repeated(span())),
            "schema_url": draw(pb_string()),
        }, ScopeSpans)
    
    @composite
    def resource_spans(draw):
        return EncodeWithArgs({
            "resource": draw(resource()),
            "scope_spans": draw(pb_repeated(scope_spans())),
            "schema_url": draw(pb_string()),
        }, ResourceSpans)
    
    return EncodeWithArgs({
        "resource_spans": draw(pb_repeated(resource_spans())),
    }, TracesData)

@composite
def metrics_data(draw):
    @composite
    def exemplar(draw):
        kwargs = {}
        oneof = draw(integers(min_value=0, max_value=1))
        if oneof == 0:
            kwargs["as_double"] = draw(pb_double())
        elif oneof == 1:
            kwargs["as_int"] = draw(pb_sfixed64())

        return EncodeWithArgs({
            **kwargs,
            "time_unix_nano": draw(pb_fixed64()),
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "filtered_attributes": draw(pb_repeated(key_value())),
        }, Exemplar)
    
    @composite
    def value_at_quantile(draw):
        return EncodeWithArgs({
            "quantile": draw_pb_double(draw),
            "value": draw_pb_double(draw),
        }, ValueAtQuantile)
    
    @composite
    def summary_data_point(draw):
        return EncodeWithArgs({
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            "quantile_values": draw(pb_repeated(value_at_quantile())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
        }, SummaryDataPoint)
    
    @composite
    def buckets(draw):
        return EncodeWithArgs({
            "offset": draw(pb_sint32()),
            "bucket_counts": draw(pb_repeated(pb_uint64())),
        }, Buckets)
    
    @composite
    def exponential_histogram_data_point(draw):
        return EncodeWithArgs({
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            "positive": draw(buckets()),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
            "exemplars": draw(pb_repeated(exemplar())),
            "max": draw_pb_double(draw),
            "zero_threshold": draw_pb_double(draw),
        }, ExponentialHistogramDataPoint)
    
    @composite
    def histogram_data_point(draw):
        return EncodeWithArgs({
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            "bucket_counts": draw(pb_repeated(pb_uint64())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
            "exemplars": draw(pb_repeated(exemplar())),
            "explicit_bounds": draw(pb_repeated(pb_double())),
            "max": draw_pb_double(draw),
        }, HistogramDataPoint)
    
    @composite
    def number_data_point(draw):
        oneof = draw(integers(min_value=0, max_value=3))
        kwargs = {}
        if oneof == 0:
            kwargs["as_int"] = draw(pb_sfixed32())
        elif oneof == 1:
            kwargs["as_double"] = draw(pb_double())

        return EncodeWithArgs({
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            **kwargs,
            "exemplars": draw(pb_repeated(exemplar())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
        }, NumberDataPoint)
    
    @composite
    def summary(draw):
        return EncodeWithArgs({
            "data_points": draw(pb_repeated(summary_data_point())),
        }, Summary)
    
    @composite
    def exponential_histogram(draw):
        return EncodeWithArgs({
            "data_points": draw(pb_repeated(exponential_histogram_data_point())),
            "aggregation_temporality": draw(pb_enum(metrics_sf.AggregationTemporality)),
        }, ExponentialHistogram)
    
    @composite
    def histogram(draw):
        return EncodeWithArgs({
            "data_points": draw(pb_repeated(histogram_data_point())),
            "aggregation_temporality": draw(pb_enum(metrics_sf.AggregationTemporality)),
        }, Histogram)
    
    @composite
    def sum(draw):
        return EncodeWithArgs({
            "data_points": draw(pb_repeated(number_data_point())),
            "aggregation_temporality": draw(pb_enum(metrics_sf.AggregationTemporality)),
            "is_monotonic": draw(pb_bool()),
        }, Sum)
    
    @composite
    def gauge(draw):
        return EncodeWithArgs({
            "data_points": draw(pb_repeated(number_data_point())),
        }, Gauge)
    
    @composite
    def metric(draw):
        oneof = draw(integers(min_value=0, max_value=3))
        kwargs = {}
        if oneof == 0:
            kwargs["gauge"] = draw(gauge())
        elif oneof == 1:
            kwargs["sum"] = draw(sum())
        elif oneof == 2:
            kwargs["histogram"] = draw(histogram())
        elif oneof == 3:
            kwargs["exponential_histogram"] = draw(exponential_histogram())

        return EncodeWithArgs({
            "name": draw(pb_string()),
            "description": draw(pb_string()),
            "unit": draw(pb_string()),
            **kwargs,
            "metadata": draw(pb_repeated(key_value())),
        }, Metric)
    
    @composite
    def scope_metrics(draw):
        return EncodeWithArgs({
            "scope": draw(instrumentation_scope()),
            "metrics": draw(pb_repeated(metric())),
            "schema_url": draw(pb_string()),
        }, ScopeMetrics)
    
    @composite
    def resource_metrics(draw):
        return EncodeWithArgs({
            "resource": draw(resource()),
            "scope_metrics": draw(pb_repeated(scope_metrics())),
            "schema_url": draw(pb_string()),
        }, ResourceMetrics)
    
    return EncodeWithArgs({
        "resource_metrics": draw(pb_repeated(resource_metrics())),
    }, MetricsData)


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
    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(logs_data())
    def test_log_data(self, logs_data):
        self.assertEqual(
            encode_recurse(logs_data, "pb2").SerializeToString(deterministic=True),
            bytes(encode_recurse(logs_data, "sf"))
        )

    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(traces_data())
    def test_trace_data(self, traces_data):
        self.assertEqual(
            encode_recurse(traces_data, "pb2").SerializeToString(deterministic=True),
            bytes(encode_recurse(traces_data, "sf"))
        )

    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(metrics_data())
    def test_metrics_data(self, metrics_data):
        self.assertEqual(
            encode_recurse(metrics_data, "pb2").SerializeToString(deterministic=True),
            bytes(encode_recurse(metrics_data, "sf"))
        )
