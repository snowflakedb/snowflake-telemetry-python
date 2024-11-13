from __future__ import annotations

from typing import (
    Any, 
    Dict, 
    List,
    Mapping,
)
import unittest
import hypothesis
import hypothesis.control as hc
import hypothesis.strategies as st

import opentelemetry.proto.logs.v1.logs_pb2 as logs_pb2
import opentelemetry.proto.trace.v1.trace_pb2 as trace_pb2
import opentelemetry.proto.common.v1.common_pb2 as common_pb2
import opentelemetry.proto.metrics.v1.metrics_pb2 as metrics_pb2
import opentelemetry.proto.resource.v1.resource_pb2 as resource_pb2

import snowflake.telemetry._internal.opentelemetry.proto.logs.v1.logs_marshaler as logs_sf
import snowflake.telemetry._internal.opentelemetry.proto.trace.v1.trace_marshaler as trace_sf
import snowflake.telemetry._internal.opentelemetry.proto.common.v1.common_marshaler as common_sf
import snowflake.telemetry._internal.opentelemetry.proto.metrics.v1.metrics_marshaler as metrics_sf
import snowflake.telemetry._internal.opentelemetry.proto.resource.v1.resource_marshaler as resource_sf

# Strategy for generating protobuf types
def nullable(type): return st.one_of(st.none(), type)
def pb_uint32(): return nullable(st.integers(min_value=0, max_value=2**32-1))
def pb_uint64(): return nullable(st.integers(min_value=0, max_value=2**64-1))
def pb_int32(): return nullable(st.integers(min_value=-2**31, max_value=2**31-1))
def pb_int64(): return nullable(st.integers(min_value=-2**63, max_value=2**63-1))
def pb_sint32(): return nullable(st.integers(min_value=-2**31, max_value=2**31-1))
def pb_sint64(): return nullable(st.integers(min_value=-2**63, max_value=2**63-1))
def pb_float(): return nullable(st.floats(allow_nan=False, allow_infinity=False, width=32))
def pb_double(): return nullable(st.floats(allow_nan=False, allow_infinity=False, width=64))
def draw_pb_double(draw):
    # -0.0 is an edge case that is not handled by the custom serialization library
    double = draw(pb_double())
    hc.assume(str(double) != "-0.0")
    return double
def pb_fixed64(): return pb_uint64()
def pb_fixed32(): return pb_uint32()
def pb_sfixed64(): return pb_int64()
def pb_sfixed32(): return pb_int32()
def pb_bool(): return nullable(st.booleans())
def pb_string(): return nullable(st.text(max_size=20))
def pb_bytes(): return nullable(st.binary(max_size=20))
def draw_pb_enum(draw, enum): 
    # Sample int val of enum, will be converted to member in encode_recurse
    # Sample from pb2 values as it is the source of truth
    return draw(nullable(st.sampled_from([member for member in enum.values()])))
def pb_repeated(type): return nullable(st.lists(type, max_size=3)) # limit the size of the repeated field to speed up testing
def pb_span_id(): return nullable(st.binary(min_size=8, max_size=8))
def pb_trace_id(): return nullable(st.binary(min_size=16, max_size=16))
# For drawing oneof fields
# call with pb_oneof(draw, field1=pb_type1_callable, field2=pb_type2_callable, ...)
def pb_oneof(draw, **kwargs):
    n = len(kwargs)
    r = draw(st.integers(min_value=0, max_value=n-1))
    k, v = list(kwargs.items())[r]
    return {k: draw(v())}
def pb_message(type):
    return nullable(type)

SF = "_sf"
PB = "_pb2"

# Strategies for generating opentelemetry-proto types
@st.composite
def instrumentation_scope(draw):
    return {
        SF: common_sf.InstrumentationScope,
        PB: common_pb2.InstrumentationScope,
        "name": draw(pb_string()),
        "version": draw(pb_string()),
        "attributes": draw(pb_repeated(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
    }

@st.composite
def resource(draw):
    return {
        SF: resource_sf.Resource,
        PB: resource_pb2.Resource,
        "attributes": draw(pb_repeated(key_value())),
        "dropped_attributes_count": draw(pb_uint32()),
    }

@st.composite
def any_value(draw):
    return {
        SF: common_sf.AnyValue,
        PB: common_pb2.AnyValue,
        **pb_oneof(
            draw,
            string_value=pb_string,
            bool_value=pb_bool,
            int_value=pb_int64,
            double_value=pb_double,
            array_value=array_value,
            kvlist_value=key_value_list,
            bytes_value=pb_bytes,
        ),
    }

@st.composite
def array_value(draw):
    return {
        SF: common_sf.ArrayValue,
        PB: common_pb2.ArrayValue,
        "values": draw(pb_repeated(any_value())),
    }

@st.composite
def key_value(draw):
    return {
        SF: common_sf.KeyValue,
        PB: common_pb2.KeyValue,
        "key": draw(pb_string()),
        "value": draw(any_value()),
    }

@st.composite
def key_value_list(draw):
    return {
        SF: common_sf.KeyValueList,
        PB: common_pb2.KeyValueList,
        "values": draw(pb_repeated(key_value())),
    }

@st.composite
def logs_data(draw):
    @st.composite
    def log_record(draw):
        return {
            SF: logs_sf.LogRecord,
            PB: logs_pb2.LogRecord,
            "time_unix_nano": draw(pb_fixed64()),
            "observed_time_unix_nano": draw(pb_fixed64()),
            "severity_number": draw_pb_enum(draw, logs_pb2.SeverityNumber),
            "severity_text": draw(pb_string()),
            "body": draw(pb_message(any_value())),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
            "span_id": draw(pb_span_id()),
            "trace_id": draw(pb_trace_id()),
        }

    @st.composite
    def scope_logs(draw):
        return {
            SF: logs_sf.ScopeLogs,
            PB: logs_pb2.ScopeLogs,
            "scope": draw(pb_message(instrumentation_scope())),
            "log_records": draw(pb_repeated(log_record())),
            "schema_url": draw(pb_string()),
        }

    @st.composite
    def resource_logs(draw):
        return {
            SF: logs_sf.ResourceLogs,
            PB: logs_pb2.ResourceLogs,
            "resource": draw(pb_message(resource())),
            "scope_logs": draw(pb_repeated(scope_logs())),
            "schema_url": draw(pb_string()),
        }
    
    return {
        SF: logs_sf.LogsData,
        PB: logs_pb2.LogsData,
        "resource_logs": draw(pb_repeated(resource_logs())),
    }

@st.composite
def traces_data(draw):
    @st.composite
    def event(draw):
        return {
            SF: trace_sf.Span.Event,
            PB: trace_pb2.Span.Event,
            "time_unix_nano": draw(pb_fixed64()),
            "name": draw(pb_string()),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
        }
    
    @st.composite
    def link(draw):
        return {
            SF: trace_sf.Span.Link,
            PB: trace_pb2.Span.Link,
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "trace_state": draw(pb_string()),
            "attributes": draw(pb_repeated(key_value())),
            "dropped_attributes_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
        }
    
    @st.composite
    def status(draw):
        return {
            SF: trace_sf.Status,
            PB: trace_pb2.Status,
            "code": draw_pb_enum(draw, trace_pb2.Status.StatusCode),
            "message": draw(pb_string()),
        }
    
    @st.composite
    def span(draw):
        return {
            SF: trace_sf.Span,
            PB: trace_pb2.Span,
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "trace_state": draw(pb_string()),
            "parent_span_id": draw(pb_span_id()),
            "name": draw(pb_string()),
            "kind": draw_pb_enum(draw, trace_pb2.Span.SpanKind),
            "start_time_unix_nano": draw(pb_fixed64()),
            "end_time_unix_nano": draw(pb_fixed64()),
            "attributes": draw(pb_repeated(key_value())),
            "events": draw(pb_repeated(event())),
            "links": draw(pb_repeated(link())),
            "status": draw(pb_message(status())),
            "dropped_attributes_count": draw(pb_uint32()),
            "dropped_events_count": draw(pb_uint32()),
            "dropped_links_count": draw(pb_uint32()),
            "flags": draw(pb_fixed32()),
        }

    @st.composite
    def scope_spans(draw):
        return {
            SF: trace_sf.ScopeSpans,
            PB: trace_pb2.ScopeSpans,
            "scope": draw(pb_message(instrumentation_scope())),
            "spans": draw(pb_repeated(span())),
            "schema_url": draw(pb_string()),
        }

    @st.composite
    def resource_spans(draw):
        return {
            SF: trace_sf.ResourceSpans,
            PB: trace_pb2.ResourceSpans,
            "resource": draw(pb_message(resource())),
            "scope_spans": draw(pb_repeated(scope_spans())),
            "schema_url": draw(pb_string()),
        }

    return {
        SF: trace_sf.TracesData,
        PB: trace_pb2.TracesData,
        "resource_spans": draw(pb_repeated(resource_spans())),
    }

@st.composite
def metrics_data(draw):
    @st.composite
    def exemplar(draw):
        return {
            SF: metrics_sf.Exemplar,
            PB: metrics_pb2.Exemplar,
            **pb_oneof(
                draw,
                as_double=pb_double,
                as_int=pb_sfixed64,
            ),
            "time_unix_nano": draw(pb_fixed64()),
            "trace_id": draw(pb_trace_id()),
            "span_id": draw(pb_span_id()),
            "filtered_attributes": draw(pb_repeated(key_value())),
        }
    
    @st.composite
    def value_at_quantile(draw):
        return {
            SF: metrics_sf.SummaryDataPoint.ValueAtQuantile,
            PB: metrics_pb2.SummaryDataPoint.ValueAtQuantile,
            "quantile": draw_pb_double(draw),
            "value": draw_pb_double(draw),
        }
    
    @st.composite
    def summary_data_point(draw):
        return {
            SF: metrics_sf.SummaryDataPoint,
            PB: metrics_pb2.SummaryDataPoint,
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            "quantile_values": draw(pb_repeated(value_at_quantile())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
        }
    
    @st.composite
    def buckets(draw):
        return {
            SF: metrics_sf.ExponentialHistogramDataPoint.Buckets,
            PB: metrics_pb2.ExponentialHistogramDataPoint.Buckets,
            "offset": draw(pb_sint32()),
            "bucket_counts": draw(pb_repeated(pb_uint64())),
        }
    
    @st.composite
    def exponential_histogram_data_point(draw):
        return {
            SF: metrics_sf.ExponentialHistogramDataPoint,
            PB: metrics_pb2.ExponentialHistogramDataPoint,
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            **pb_oneof(
                draw,
                positive=buckets,
                negative=buckets,
            ),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
            "exemplars": draw(pb_repeated(exemplar())),
            "max": draw_pb_double(draw),
            "zero_threshold": draw_pb_double(draw),
        }
    
    @st.composite
    def histogram_data_point(draw):
        return {
            SF: metrics_sf.HistogramDataPoint,
            PB: metrics_pb2.HistogramDataPoint,
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            "count": draw(pb_fixed64()),
            "sum": draw_pb_double(draw),
            "bucket_counts": draw(pb_repeated(pb_uint64())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
            "exemplars": draw(pb_repeated(exemplar())),
            "explicit_bounds": draw(pb_repeated(pb_double())),
            **pb_oneof(
                draw,
                max=pb_double,
                min=pb_double,
            ),
        }
    
    @st.composite
    def number_data_point(draw):
        return {
            SF: metrics_sf.NumberDataPoint,
            PB: metrics_pb2.NumberDataPoint,
            "start_time_unix_nano": draw(pb_fixed64()),
            "time_unix_nano": draw(pb_fixed64()),
            **pb_oneof(
                draw,
                as_int=pb_sfixed64,
                as_double=pb_double,
            ),
            "exemplars": draw(pb_repeated(exemplar())),
            "attributes": draw(pb_repeated(key_value())),
            "flags": draw(pb_uint32()),
        }
    
    @st.composite
    def summary(draw):
        return {
            SF: metrics_sf.Summary,
            PB: metrics_pb2.Summary,
            "data_points": draw(pb_repeated(summary_data_point())),
        }
    
    @st.composite
    def exponential_histogram(draw):
        return {
            SF: metrics_sf.ExponentialHistogram,
            PB: metrics_pb2.ExponentialHistogram,
            "data_points": draw(pb_repeated(exponential_histogram_data_point())),
            "aggregation_temporality": draw_pb_enum(draw, metrics_pb2.AggregationTemporality),
        }
    
    @st.composite
    def histogram(draw):
        return {
            SF: metrics_sf.Histogram,
            PB: metrics_pb2.Histogram,
            "data_points": draw(pb_repeated(histogram_data_point())),
            "aggregation_temporality": draw_pb_enum(draw, metrics_pb2.AggregationTemporality),
        }
    
    @st.composite
    def sum(draw):
        return {
            SF: metrics_sf.Sum,
            PB: metrics_pb2.Sum,
            "data_points": draw(pb_repeated(number_data_point())),
            "aggregation_temporality": draw_pb_enum(draw, metrics_pb2.AggregationTemporality),
            "is_monotonic": draw(pb_bool()),
        }
    
    @st.composite
    def gauge(draw):
        return {
            SF: metrics_sf.Gauge,
            PB: metrics_pb2.Gauge,
            "data_points": draw(pb_repeated(number_data_point())),
        }
    
    @st.composite
    def metric(draw):
        return {
            SF: metrics_sf.Metric,
            PB: metrics_pb2.Metric,
            "name": draw(pb_string()),
            "description": draw(pb_string()),
            "unit": draw(pb_string()),
            **pb_oneof(
                draw,
                gauge=gauge,
                sum=sum,
                summary=summary,
                histogram=histogram,
                exponential_histogram=exponential_histogram,
            ),
            "metadata": draw(pb_repeated(key_value())),
        }
    
    @st.composite
    def scope_metrics(draw):
        return {
            SF: metrics_sf.ScopeMetrics,
            PB: metrics_pb2.ScopeMetrics,
            "scope": draw(pb_message(instrumentation_scope())),
            "metrics": draw(pb_repeated(metric())),
            "schema_url": draw(pb_string()),
        }
    
    @st.composite
    def resource_metrics(draw):
        return {
            SF: metrics_sf.ResourceMetrics,
            PB: metrics_pb2.ResourceMetrics,
            "resource": draw(pb_message(resource())),
            "scope_metrics": draw(pb_repeated(scope_metrics())),
            "schema_url": draw(pb_string()),
        }
    
    return {
        SF: metrics_sf.MetricsData,
        PB: metrics_pb2.MetricsData,
        "resource_metrics": draw(pb_repeated(resource_metrics())),
    }


# Helper functions to recursively encode protobuf types using the generated args 
# and the given serialization strategy
def encode_recurse(obj: Dict[str, Any], strategy: str) -> Any:
    kwargs = {}
    for key, value in obj.items():
        if key in [SF, PB]:
            continue
        elif value is None:
            continue
        elif isinstance(value, Mapping):
            kwargs[key] = encode_recurse(value, strategy)
        elif isinstance(value, List) and value and isinstance(value[0], Mapping):
            kwargs[key] = [encode_recurse(v, strategy) for v in value if v is not None]
        elif isinstance(value, List):
            kwargs[key] = [v for v in value if v is not None]
        else:
            kwargs[key] = value
    return obj[strategy](**kwargs)

class TestProtoSerialization(unittest.TestCase):
    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(logs_data())
    def test_log_data(self, logs_data):
        self.assertEqual(
            encode_recurse(logs_data, PB).SerializeToString(deterministic=True),
            bytes(encode_recurse(logs_data, SF))
        )

    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(traces_data())
    def test_trace_data(self, traces_data):
        self.assertEqual(
            encode_recurse(traces_data, PB).SerializeToString(deterministic=True),
            bytes(encode_recurse(traces_data, SF))
        )

    @hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.too_slow])
    @hypothesis.given(metrics_data())
    def test_metrics_data(self, metrics_data):
        self.assertEqual(
            encode_recurse(metrics_data, PB).SerializeToString(deterministic=True),
            bytes(encode_recurse(metrics_data, SF))
        )
