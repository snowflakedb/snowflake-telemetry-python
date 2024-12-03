from typing import Sequence

from snowflake.telemetry.test.metrictestutil import _generate_gauge, _generate_sum

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk._logs import LogData, LogLimits, LogRecord

from opentelemetry.sdk.metrics.export import (
    AggregationTemporality, 
    Buckets,
    ExponentialHistogram,
    Histogram,
    ExponentialHistogramDataPoint,
    HistogramDataPoint,
    Metric,
    MetricsData,
    ResourceMetrics,
    ScopeMetrics,
)

from opentelemetry.sdk.trace import Event, SpanContext, _Span
from opentelemetry.trace import SpanKind, Link, TraceFlags
from opentelemetry.trace.status import Status, StatusCode



def get_logs_data() -> Sequence[LogData]:
    log1 = LogData(
        log_record=LogRecord(
            timestamp=1644650195189786880,
            observed_timestamp=1644660000000000000,
            trace_id=89564621134313219400156819398935297684,
            span_id=1312458408527513268,
            trace_flags=TraceFlags(0x01),
            severity_text="WARN",
            severity_number=SeverityNumber.WARN,
            body="Do not go gentle into that good night. Rage, rage against the dying of the light",
            resource=Resource(
                {"first_resource": "value"},
                "resource_schema_url",
            ),
            attributes={"a": 1, "b": "c"},
        ),
        instrumentation_scope=InstrumentationScope(
            "first_name", "first_version"
        ),
    )

    log2 = LogData(
        log_record=LogRecord(
            timestamp=1644650249738562048,
            observed_timestamp=1644660000000000000,
            trace_id=0,
            span_id=0,
            trace_flags=TraceFlags.DEFAULT,
            severity_text="WARN",
            severity_number=SeverityNumber.WARN,
            body="Cooper, this is no time for caution!",
            resource=Resource({"second_resource": "CASE"}),
            attributes={},
        ),
        instrumentation_scope=InstrumentationScope(
            "second_name", "second_version"
        ),
    )

    log3 = LogData(
        log_record=LogRecord(
            timestamp=1644650427658989056,
            observed_timestamp=1644660000000000000,
            trace_id=271615924622795969659406376515024083555,
            span_id=4242561578944770265,
            trace_flags=TraceFlags(0x01),
            severity_text="DEBUG",
            severity_number=SeverityNumber.DEBUG,
            body="To our galaxy",
            resource=Resource({"second_resource": "CASE"}),
            attributes={"a": 1, "b": "c"},
        ),
        instrumentation_scope=None,
    )

    log4 = LogData(
        log_record=LogRecord(
            timestamp=1644650584292683008,
            observed_timestamp=1644660000000000000,
            trace_id=212592107417388365804938480559624925555,
            span_id=6077757853989569223,
            trace_flags=TraceFlags(0x01),
            severity_text="INFO",
            severity_number=SeverityNumber.INFO,
            body="Love is the one thing that transcends time and space",
            resource=Resource(
                {"first_resource": "value"},
                "resource_schema_url",
            ),
            attributes={"filename": "model.py", "func_name": "run_method"},
        ),
        instrumentation_scope=InstrumentationScope(
            "another_name", "another_version"
        ),
    )

    return [log1, log2, log3, log4]

def get_logs_data_4MB() -> Sequence[LogData]:
    out = []
    for _ in range(8000):
        out.extend(get_logs_data())
    return out

HISTOGRAM = Metric(
    name="histogram",
    description="foo",
    unit="s",
    data=Histogram(
        data_points=[
            HistogramDataPoint(
                attributes={"a": 1, "b": True},
                start_time_unix_nano=1641946016139533244,
                time_unix_nano=1641946016139533244,
                count=5,
                sum=67,
                bucket_counts=[1, 4],
                explicit_bounds=[10.0, 20.0],
                min=8,
                max=18,
            )
        ],
        aggregation_temporality=AggregationTemporality.DELTA,
    ),
)

EXPONENTIAL_HISTOGRAM = Metric(
    name="exponential_histogram",
    description="description",
    unit="unit",
    data=ExponentialHistogram(
        data_points=[
            ExponentialHistogramDataPoint(
                attributes={"a": 1, "b": True},
                start_time_unix_nano=0,
                time_unix_nano=1,
                count=2,
                sum=3,
                scale=4,
                zero_count=5,
                positive=Buckets(offset=6, bucket_counts=[7, 8]),
                negative=Buckets(offset=9, bucket_counts=[10, 11]),
                flags=12,
                min=13.0,
                max=14.0,
            )
        ],
        aggregation_temporality=AggregationTemporality.DELTA,
    ),
)
def get_metrics_data() -> MetricsData:

    metrics = MetricsData(
        resource_metrics=[
            ResourceMetrics(
                resource=Resource(
                    attributes={"a": 1, "b": False},
                    schema_url="resource_schema_url",
                ),
                scope_metrics=[
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[HISTOGRAM, HISTOGRAM],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="second_name",
                            version="second_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[HISTOGRAM],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="third_name",
                            version="third_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[HISTOGRAM],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[_generate_sum("sum_int", 33)],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[_generate_sum("sum_double", 2.98)],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[_generate_gauge("gauge_int", 9000)],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[_generate_gauge("gauge_double", 52.028)],
                        schema_url="instrumentation_scope_schema_url",
                    ),
                    ScopeMetrics(
                        scope=InstrumentationScope(
                            name="first_name",
                            version="first_version",
                            schema_url="insrumentation_scope_schema_url",
                        ),
                        metrics=[EXPONENTIAL_HISTOGRAM],
                        schema_url="instrumentation_scope_schema_url",
                    )
                ],
                schema_url="resource_schema_url",
            )
        ]
    )

    return metrics

def get_traces_data() -> Sequence[_Span]:
    trace_id = 0x3E0C63257DE34C926F9EFCD03927272E

    base_time = 683647322 * 10**9  # in ns
    start_times = (
        base_time,
        base_time + 150 * 10**6,
        base_time + 300 * 10**6,
        base_time + 400 * 10**6,
    )
    end_times = (
        start_times[0] + (50 * 10**6),
        start_times[1] + (100 * 10**6),
        start_times[2] + (200 * 10**6),
        start_times[3] + (300 * 10**6),
    )

    parent_span_context = SpanContext(
        trace_id, 0x1111111111111111, is_remote=True
    )

    other_context = SpanContext(
        trace_id, 0x2222222222222222, is_remote=False
    )

    span1 = _Span(
        name="test-span-1",
        context=SpanContext(
            trace_id,
            0x34BF92DEEFC58C92,
            is_remote=False,
            trace_flags=TraceFlags(TraceFlags.SAMPLED),
        ),
        parent=parent_span_context,
        events=(
            Event(
                name="event0",
                timestamp=base_time + 50 * 10**6,
                attributes={
                    "annotation_bool": True,
                    "annotation_string": "annotation_test",
                    "key_float": 0.3,
                },
            ),
        ),
        links=(
            Link(context=other_context, attributes={"key_bool": True}),
        ),
        resource=Resource({}, "resource_schema_url"),
    )
    span1.start(start_time=start_times[0])
    span1.set_attribute("key_bool", False)
    span1.set_attribute("key_string", "hello_world")
    span1.set_attribute("key_float", 111.22)
    span1.set_status(Status(StatusCode.ERROR, "Example description"))
    span1.end(end_time=end_times[0])

    span2 = _Span(
        name="test-span-2",
        context=parent_span_context,
        parent=None,
        resource=Resource(attributes={"key_resource": "some_resource"}),
    )
    span2.start(start_time=start_times[1])
    span2.end(end_time=end_times[1])

    span3 = _Span(
        name="test-span-3",
        context=other_context,
        parent=None,
        resource=Resource(attributes={"key_resource": "some_resource"}),
    )
    span3.start(start_time=start_times[2])
    span3.set_attribute("key_string", "hello_world")
    span3.end(end_time=end_times[2])

    span4 = _Span(
        name="test-span-4",
        context=other_context,
        parent=None,
        resource=Resource({}, "resource_schema_url"),
        instrumentation_scope=InstrumentationScope(
            name="name", version="version"
        ),
    )
    span4.start(start_time=start_times[3])
    span4.end(end_time=end_times[3])

    return [span1, span2, span3, span4]