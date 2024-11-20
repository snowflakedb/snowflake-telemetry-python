# Generated by the protoc compiler with a custom plugin. DO NOT EDIT!
# sources: opentelemetry/proto/metrics/v1/metrics.proto

from __future__ import annotations

import struct
from typing import List

from snowflake.telemetry._internal.opentelemetry.proto.common.v1.common_marshaler import *
from snowflake.telemetry._internal.opentelemetry.proto.resource.v1.resource_marshaler import *
from snowflake.telemetry._internal.serialize import (
    Enum,
    MessageMarshaler,
    Varint,
)


class AggregationTemporality(Enum):
    AGGREGATION_TEMPORALITY_UNSPECIFIED = 0
    AGGREGATION_TEMPORALITY_DELTA = 1
    AGGREGATION_TEMPORALITY_CUMULATIVE = 2


class DataPointFlags(Enum):
    DATA_POINT_FLAGS_DO_NOT_USE = 0
    DATA_POINT_FLAGS_NO_RECORDED_VALUE_MASK = 1


class MetricsData(MessageMarshaler):
    @property
    def resource_metrics(self) -> List[ResourceMetrics]:
        if self._resource_metrics is None:
            self._resource_metrics = list()
        return self._resource_metrics

    def __init__(
        self,
        resource_metrics: List[ResourceMetrics] = None,
    ):
        self._resource_metrics: List[ResourceMetrics] = resource_metrics

    def calculate_size(self) -> int:
        size = 0
        if self._resource_metrics:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._resource_metrics
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._resource_metrics:
            for v in self._resource_metrics:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class ResourceMetrics(MessageMarshaler):
    @property
    def resource(self) -> Resource:
        if self._resource is None:
            self._resource = Resource()
        return self._resource

    @property
    def scope_metrics(self) -> List[ScopeMetrics]:
        if self._scope_metrics is None:
            self._scope_metrics = list()
        return self._scope_metrics

    schema_url: str

    def __init__(
        self,
        resource: Resource = None,
        scope_metrics: List[ScopeMetrics] = None,
        schema_url: str = "",
    ):
        self._resource: Resource = resource
        self._scope_metrics: List[ScopeMetrics] = scope_metrics
        self.schema_url: str = schema_url

    def calculate_size(self) -> int:
        size = 0
        if self._resource is not None:
            size += (
                len(b"\n")
                + Varint.size_varint_u32(self._resource._get_size())
                + self._resource._get_size()
            )
        if self._scope_metrics:
            size += sum(
                message._get_size()
                + len(b"\x12")
                + Varint.size_varint_u32(message._get_size())
                for message in self._scope_metrics
            )
        if self.schema_url:
            v = self.schema_url.encode("utf-8")
            size += len(b"\x1a") + Varint.size_varint_u32(len(v)) + len(v)
        return size

    def write_to(self, out: bytearray) -> None:
        if self._resource is not None:
            out += b"\n"
            Varint.write_varint_u32(out, self._resource._get_size())
            self._resource.write_to(out)
        if self._scope_metrics:
            for v in self._scope_metrics:
                out += b"\x12"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.schema_url:
            v = self.schema_url.encode("utf-8")
            out += b"\x1a"
            Varint.write_varint_u32(out, len(v))
            out += v


class ScopeMetrics(MessageMarshaler):
    @property
    def scope(self) -> InstrumentationScope:
        if self._scope is None:
            self._scope = InstrumentationScope()
        return self._scope

    @property
    def metrics(self) -> List[Metric]:
        if self._metrics is None:
            self._metrics = list()
        return self._metrics

    schema_url: str

    def __init__(
        self,
        scope: InstrumentationScope = None,
        metrics: List[Metric] = None,
        schema_url: str = "",
    ):
        self._scope: InstrumentationScope = scope
        self._metrics: List[Metric] = metrics
        self.schema_url: str = schema_url

    def calculate_size(self) -> int:
        size = 0
        if self._scope is not None:
            size += (
                len(b"\n")
                + Varint.size_varint_u32(self._scope._get_size())
                + self._scope._get_size()
            )
        if self._metrics:
            size += sum(
                message._get_size()
                + len(b"\x12")
                + Varint.size_varint_u32(message._get_size())
                for message in self._metrics
            )
        if self.schema_url:
            v = self.schema_url.encode("utf-8")
            size += len(b"\x1a") + Varint.size_varint_u32(len(v)) + len(v)
        return size

    def write_to(self, out: bytearray) -> None:
        if self._scope is not None:
            out += b"\n"
            Varint.write_varint_u32(out, self._scope._get_size())
            self._scope.write_to(out)
        if self._metrics:
            for v in self._metrics:
                out += b"\x12"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.schema_url:
            v = self.schema_url.encode("utf-8")
            out += b"\x1a"
            Varint.write_varint_u32(out, len(v))
            out += v


class Metric(MessageMarshaler):
    name: str
    description: str
    unit: str

    @property
    def gauge(self) -> Gauge:
        if self._gauge is None:
            self._gauge = Gauge()
        return self._gauge

    @property
    def sum(self) -> Sum:
        if self._sum is None:
            self._sum = Sum()
        return self._sum

    @property
    def histogram(self) -> Histogram:
        if self._histogram is None:
            self._histogram = Histogram()
        return self._histogram

    @property
    def exponential_histogram(self) -> ExponentialHistogram:
        if self._exponential_histogram is None:
            self._exponential_histogram = ExponentialHistogram()
        return self._exponential_histogram

    @property
    def summary(self) -> Summary:
        if self._summary is None:
            self._summary = Summary()
        return self._summary

    @property
    def metadata(self) -> List[KeyValue]:
        if self._metadata is None:
            self._metadata = list()
        return self._metadata

    def __init__(
        self,
        name: str = "",
        description: str = "",
        unit: str = "",
        gauge: Gauge = None,
        sum: Sum = None,
        histogram: Histogram = None,
        exponential_histogram: ExponentialHistogram = None,
        summary: Summary = None,
        metadata: List[KeyValue] = None,
    ):
        self.name: str = name
        self.description: str = description
        self.unit: str = unit
        self._gauge: Gauge = gauge
        self._sum: Sum = sum
        self._histogram: Histogram = histogram
        self._exponential_histogram: ExponentialHistogram = exponential_histogram
        self._summary: Summary = summary
        self._metadata: List[KeyValue] = metadata

    def calculate_size(self) -> int:
        size = 0
        if self.name:
            v = self.name.encode("utf-8")
            size += len(b"\n") + Varint.size_varint_u32(len(v)) + len(v)
        if self.description:
            v = self.description.encode("utf-8")
            size += len(b"\x12") + Varint.size_varint_u32(len(v)) + len(v)
        if self.unit:
            v = self.unit.encode("utf-8")
            size += len(b"\x1a") + Varint.size_varint_u32(len(v)) + len(v)
        if self._gauge is not None:
            size += (
                len(b"*")
                + Varint.size_varint_u32(self._gauge._get_size())
                + self._gauge._get_size()
            )
        if self._sum is not None:
            size += (
                len(b":")
                + Varint.size_varint_u32(self._sum._get_size())
                + self._sum._get_size()
            )
        if self._histogram is not None:
            size += (
                len(b"J")
                + Varint.size_varint_u32(self._histogram._get_size())
                + self._histogram._get_size()
            )
        if self._exponential_histogram is not None:
            size += (
                len(b"R")
                + Varint.size_varint_u32(self._exponential_histogram._get_size())
                + self._exponential_histogram._get_size()
            )
        if self._summary is not None:
            size += (
                len(b"Z")
                + Varint.size_varint_u32(self._summary._get_size())
                + self._summary._get_size()
            )
        if self._metadata:
            size += sum(
                message._get_size()
                + len(b"b")
                + Varint.size_varint_u32(message._get_size())
                for message in self._metadata
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self.name:
            v = self.name.encode("utf-8")
            out += b"\n"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self.description:
            v = self.description.encode("utf-8")
            out += b"\x12"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self.unit:
            v = self.unit.encode("utf-8")
            out += b"\x1a"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self._gauge is not None:
            out += b"*"
            Varint.write_varint_u32(out, self._gauge._get_size())
            self._gauge.write_to(out)
        if self._sum is not None:
            out += b":"
            Varint.write_varint_u32(out, self._sum._get_size())
            self._sum.write_to(out)
        if self._histogram is not None:
            out += b"J"
            Varint.write_varint_u32(out, self._histogram._get_size())
            self._histogram.write_to(out)
        if self._exponential_histogram is not None:
            out += b"R"
            Varint.write_varint_u32(out, self._exponential_histogram._get_size())
            self._exponential_histogram.write_to(out)
        if self._summary is not None:
            out += b"Z"
            Varint.write_varint_u32(out, self._summary._get_size())
            self._summary.write_to(out)
        if self._metadata:
            for v in self._metadata:
                out += b"b"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class Gauge(MessageMarshaler):
    @property
    def data_points(self) -> List[NumberDataPoint]:
        if self._data_points is None:
            self._data_points = list()
        return self._data_points

    def __init__(
        self,
        data_points: List[NumberDataPoint] = None,
    ):
        self._data_points: List[NumberDataPoint] = data_points

    def calculate_size(self) -> int:
        size = 0
        if self._data_points:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._data_points
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._data_points:
            for v in self._data_points:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class Sum(MessageMarshaler):
    @property
    def data_points(self) -> List[NumberDataPoint]:
        if self._data_points is None:
            self._data_points = list()
        return self._data_points

    aggregation_temporality: AggregationTemporality
    is_monotonic: bool

    def __init__(
        self,
        data_points: List[NumberDataPoint] = None,
        aggregation_temporality: AggregationTemporality = 0,
        is_monotonic: bool = False,
    ):
        self._data_points: List[NumberDataPoint] = data_points
        self.aggregation_temporality: AggregationTemporality = aggregation_temporality
        self.is_monotonic: bool = is_monotonic

    def calculate_size(self) -> int:
        size = 0
        if self._data_points:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._data_points
            )
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            size += len(b"\x10") + Varint.size_varint_u32(v)
        if self.is_monotonic:
            size += len(b"\x18") + 1
        return size

    def write_to(self, out: bytearray) -> None:
        if self._data_points:
            for v in self._data_points:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            out += b"\x10"
            Varint.write_varint_u32(out, v)
        if self.is_monotonic:
            out += b"\x18"
            Varint.write_varint_u32(out, 1 if self.is_monotonic else 0)


class Histogram(MessageMarshaler):
    @property
    def data_points(self) -> List[HistogramDataPoint]:
        if self._data_points is None:
            self._data_points = list()
        return self._data_points

    aggregation_temporality: AggregationTemporality

    def __init__(
        self,
        data_points: List[HistogramDataPoint] = None,
        aggregation_temporality: AggregationTemporality = 0,
    ):
        self._data_points: List[HistogramDataPoint] = data_points
        self.aggregation_temporality: AggregationTemporality = aggregation_temporality

    def calculate_size(self) -> int:
        size = 0
        if self._data_points:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._data_points
            )
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            size += len(b"\x10") + Varint.size_varint_u32(v)
        return size

    def write_to(self, out: bytearray) -> None:
        if self._data_points:
            for v in self._data_points:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            out += b"\x10"
            Varint.write_varint_u32(out, v)


class ExponentialHistogram(MessageMarshaler):
    @property
    def data_points(self) -> List[ExponentialHistogramDataPoint]:
        if self._data_points is None:
            self._data_points = list()
        return self._data_points

    aggregation_temporality: AggregationTemporality

    def __init__(
        self,
        data_points: List[ExponentialHistogramDataPoint] = None,
        aggregation_temporality: AggregationTemporality = 0,
    ):
        self._data_points: List[ExponentialHistogramDataPoint] = data_points
        self.aggregation_temporality: AggregationTemporality = aggregation_temporality

    def calculate_size(self) -> int:
        size = 0
        if self._data_points:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._data_points
            )
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            size += len(b"\x10") + Varint.size_varint_u32(v)
        return size

    def write_to(self, out: bytearray) -> None:
        if self._data_points:
            for v in self._data_points:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.aggregation_temporality:
            v = self.aggregation_temporality
            if not isinstance(v, int):
                v = v.value
            out += b"\x10"
            Varint.write_varint_u32(out, v)


class Summary(MessageMarshaler):
    @property
    def data_points(self) -> List[SummaryDataPoint]:
        if self._data_points is None:
            self._data_points = list()
        return self._data_points

    def __init__(
        self,
        data_points: List[SummaryDataPoint] = None,
    ):
        self._data_points: List[SummaryDataPoint] = data_points

    def calculate_size(self) -> int:
        size = 0
        if self._data_points:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._data_points
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._data_points:
            for v in self._data_points:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class NumberDataPoint(MessageMarshaler):
    start_time_unix_nano: int
    time_unix_nano: int
    as_double: float

    @property
    def exemplars(self) -> List[Exemplar]:
        if self._exemplars is None:
            self._exemplars = list()
        return self._exemplars

    as_int: int

    @property
    def attributes(self) -> List[KeyValue]:
        if self._attributes is None:
            self._attributes = list()
        return self._attributes

    flags: int

    def __init__(
        self,
        start_time_unix_nano: int = 0,
        time_unix_nano: int = 0,
        as_double: float = None,
        exemplars: List[Exemplar] = None,
        as_int: int = None,
        attributes: List[KeyValue] = None,
        flags: int = 0,
    ):
        self.start_time_unix_nano: int = start_time_unix_nano
        self.time_unix_nano: int = time_unix_nano
        self.as_double: float = as_double
        self._exemplars: List[Exemplar] = exemplars
        self.as_int: int = as_int
        self._attributes: List[KeyValue] = attributes
        self.flags: int = flags

    def calculate_size(self) -> int:
        size = 0
        if self.start_time_unix_nano:
            size += len(b"\x11") + 8
        if self.time_unix_nano:
            size += len(b"\x19") + 8
        if self.as_double is not None:
            size += len(b"!") + 8
        if self._exemplars:
            size += sum(
                message._get_size()
                + len(b"*")
                + Varint.size_varint_u32(message._get_size())
                for message in self._exemplars
            )
        if self.as_int is not None:
            size += len(b"1") + 8
        if self._attributes:
            size += sum(
                message._get_size()
                + len(b":")
                + Varint.size_varint_u32(message._get_size())
                for message in self._attributes
            )
        if self.flags:
            size += len(b"@") + Varint.size_varint_u32(self.flags)
        return size

    def write_to(self, out: bytearray) -> None:
        if self.start_time_unix_nano:
            out += b"\x11"
            out += struct.pack("<Q", self.start_time_unix_nano)
        if self.time_unix_nano:
            out += b"\x19"
            out += struct.pack("<Q", self.time_unix_nano)
        if self.as_double is not None:
            out += b"!"
            out += struct.pack("<d", self.as_double)
        if self._exemplars:
            for v in self._exemplars:
                out += b"*"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.as_int is not None:
            out += b"1"
            out += struct.pack("<q", self.as_int)
        if self._attributes:
            for v in self._attributes:
                out += b":"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.flags:
            out += b"@"
            Varint.write_varint_u32(out, self.flags)


class HistogramDataPoint(MessageMarshaler):
    start_time_unix_nano: int
    time_unix_nano: int
    count: int
    sum: float

    @property
    def bucket_counts(self) -> List[int]:
        if self._bucket_counts is None:
            self._bucket_counts = list()
        return self._bucket_counts

    @property
    def explicit_bounds(self) -> List[float]:
        if self._explicit_bounds is None:
            self._explicit_bounds = list()
        return self._explicit_bounds

    @property
    def exemplars(self) -> List[Exemplar]:
        if self._exemplars is None:
            self._exemplars = list()
        return self._exemplars

    @property
    def attributes(self) -> List[KeyValue]:
        if self._attributes is None:
            self._attributes = list()
        return self._attributes

    flags: int
    min: float
    max: float

    def __init__(
        self,
        start_time_unix_nano: int = 0,
        time_unix_nano: int = 0,
        count: int = 0,
        sum: float = None,
        bucket_counts: List[int] = None,
        explicit_bounds: List[float] = None,
        exemplars: List[Exemplar] = None,
        attributes: List[KeyValue] = None,
        flags: int = 0,
        min: float = None,
        max: float = None,
    ):
        self.start_time_unix_nano: int = start_time_unix_nano
        self.time_unix_nano: int = time_unix_nano
        self.count: int = count
        self.sum: float = sum
        self._bucket_counts: List[int] = bucket_counts
        self._explicit_bounds: List[float] = explicit_bounds
        self._exemplars: List[Exemplar] = exemplars
        self._attributes: List[KeyValue] = attributes
        self.flags: int = flags
        self.min: float = min
        self.max: float = max

    def calculate_size(self) -> int:
        size = 0
        if self.start_time_unix_nano:
            size += len(b"\x11") + 8
        if self.time_unix_nano:
            size += len(b"\x19") + 8
        if self.count:
            size += len(b"!") + 8
        if self.sum is not None:
            size += len(b")") + 8
        if self._bucket_counts:
            size += (
                len(b"2")
                + len(self._bucket_counts) * 8
                + Varint.size_varint_u32(len(self._bucket_counts) * 8)
            )
        if self._explicit_bounds:
            size += (
                len(b":")
                + len(self._explicit_bounds) * 8
                + Varint.size_varint_u32(len(self._explicit_bounds) * 8)
            )
        if self._exemplars:
            size += sum(
                message._get_size()
                + len(b"B")
                + Varint.size_varint_u32(message._get_size())
                for message in self._exemplars
            )
        if self._attributes:
            size += sum(
                message._get_size()
                + len(b"J")
                + Varint.size_varint_u32(message._get_size())
                for message in self._attributes
            )
        if self.flags:
            size += len(b"P") + Varint.size_varint_u32(self.flags)
        if self.min is not None:
            size += len(b"Y") + 8
        if self.max is not None:
            size += len(b"a") + 8
        return size

    def write_to(self, out: bytearray) -> None:
        if self.start_time_unix_nano:
            out += b"\x11"
            out += struct.pack("<Q", self.start_time_unix_nano)
        if self.time_unix_nano:
            out += b"\x19"
            out += struct.pack("<Q", self.time_unix_nano)
        if self.count:
            out += b"!"
            out += struct.pack("<Q", self.count)
        if self.sum is not None:
            out += b")"
            out += struct.pack("<d", self.sum)
        if self._bucket_counts:
            out += b"2"
            Varint.write_varint_u32(out, len(self._bucket_counts) * 8)
            for v in self._bucket_counts:
                out += struct.pack("<Q", v)
        if self._explicit_bounds:
            out += b":"
            Varint.write_varint_u32(out, len(self._explicit_bounds) * 8)
            for v in self._explicit_bounds:
                out += struct.pack("<d", v)
        if self._exemplars:
            for v in self._exemplars:
                out += b"B"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self._attributes:
            for v in self._attributes:
                out += b"J"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.flags:
            out += b"P"
            Varint.write_varint_u32(out, self.flags)
        if self.min is not None:
            out += b"Y"
            out += struct.pack("<d", self.min)
        if self.max is not None:
            out += b"a"
            out += struct.pack("<d", self.max)


class ExponentialHistogramDataPoint(MessageMarshaler):
    @property
    def attributes(self) -> List[KeyValue]:
        if self._attributes is None:
            self._attributes = list()
        return self._attributes

    start_time_unix_nano: int
    time_unix_nano: int
    count: int
    sum: float
    scale: int
    zero_count: int

    @property
    def positive(self) -> ExponentialHistogramDataPoint.Buckets:
        if self._positive is None:
            self._positive = ExponentialHistogramDataPoint.Buckets()
        return self._positive

    @property
    def negative(self) -> ExponentialHistogramDataPoint.Buckets:
        if self._negative is None:
            self._negative = ExponentialHistogramDataPoint.Buckets()
        return self._negative

    flags: int

    @property
    def exemplars(self) -> List[Exemplar]:
        if self._exemplars is None:
            self._exemplars = list()
        return self._exemplars

    min: float
    max: float
    zero_threshold: float

    def __init__(
        self,
        attributes: List[KeyValue] = None,
        start_time_unix_nano: int = 0,
        time_unix_nano: int = 0,
        count: int = 0,
        sum: float = None,
        scale: int = 0,
        zero_count: int = 0,
        positive: ExponentialHistogramDataPoint.Buckets = None,
        negative: ExponentialHistogramDataPoint.Buckets = None,
        flags: int = 0,
        exemplars: List[Exemplar] = None,
        min: float = None,
        max: float = None,
        zero_threshold: float = 0.0,
    ):
        self._attributes: List[KeyValue] = attributes
        self.start_time_unix_nano: int = start_time_unix_nano
        self.time_unix_nano: int = time_unix_nano
        self.count: int = count
        self.sum: float = sum
        self.scale: int = scale
        self.zero_count: int = zero_count
        self._positive: ExponentialHistogramDataPoint.Buckets = positive
        self._negative: ExponentialHistogramDataPoint.Buckets = negative
        self.flags: int = flags
        self._exemplars: List[Exemplar] = exemplars
        self.min: float = min
        self.max: float = max
        self.zero_threshold: float = zero_threshold

    def calculate_size(self) -> int:
        size = 0
        if self._attributes:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._attributes
            )
        if self.start_time_unix_nano:
            size += len(b"\x11") + 8
        if self.time_unix_nano:
            size += len(b"\x19") + 8
        if self.count:
            size += len(b"!") + 8
        if self.sum is not None:
            size += len(b")") + 8
        if self.scale:
            size += len(b"0") + Varint.size_varint_s32(self.scale)
        if self.zero_count:
            size += len(b"9") + 8
        if self._positive is not None:
            size += (
                len(b"B")
                + Varint.size_varint_u32(self._positive._get_size())
                + self._positive._get_size()
            )
        if self._negative is not None:
            size += (
                len(b"J")
                + Varint.size_varint_u32(self._negative._get_size())
                + self._negative._get_size()
            )
        if self.flags:
            size += len(b"P") + Varint.size_varint_u32(self.flags)
        if self._exemplars:
            size += sum(
                message._get_size()
                + len(b"Z")
                + Varint.size_varint_u32(message._get_size())
                for message in self._exemplars
            )
        if self.min is not None:
            size += len(b"a") + 8
        if self.max is not None:
            size += len(b"i") + 8
        if self.zero_threshold:
            size += len(b"q") + 8
        return size

    def write_to(self, out: bytearray) -> None:
        if self._attributes:
            for v in self._attributes:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.start_time_unix_nano:
            out += b"\x11"
            out += struct.pack("<Q", self.start_time_unix_nano)
        if self.time_unix_nano:
            out += b"\x19"
            out += struct.pack("<Q", self.time_unix_nano)
        if self.count:
            out += b"!"
            out += struct.pack("<Q", self.count)
        if self.sum is not None:
            out += b")"
            out += struct.pack("<d", self.sum)
        if self.scale:
            out += b"0"
            Varint.write_varint_s32(out, self.scale)
        if self.zero_count:
            out += b"9"
            out += struct.pack("<Q", self.zero_count)
        if self._positive is not None:
            out += b"B"
            Varint.write_varint_u32(out, self._positive._get_size())
            self._positive.write_to(out)
        if self._negative is not None:
            out += b"J"
            Varint.write_varint_u32(out, self._negative._get_size())
            self._negative.write_to(out)
        if self.flags:
            out += b"P"
            Varint.write_varint_u32(out, self.flags)
        if self._exemplars:
            for v in self._exemplars:
                out += b"Z"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.min is not None:
            out += b"a"
            out += struct.pack("<d", self.min)
        if self.max is not None:
            out += b"i"
            out += struct.pack("<d", self.max)
        if self.zero_threshold:
            out += b"q"
            out += struct.pack("<d", self.zero_threshold)

    class Buckets(MessageMarshaler):
        offset: int

        @property
        def bucket_counts(self) -> List[int]:
            if self._bucket_counts is None:
                self._bucket_counts = list()
            return self._bucket_counts

        def __init__(
            self,
            offset: int = 0,
            bucket_counts: List[int] = None,
        ):
            self.offset: int = offset
            self._bucket_counts: List[int] = bucket_counts

        def calculate_size(self) -> int:
            size = 0
            if self.offset:
                size += len(b"\x08") + Varint.size_varint_s32(self.offset)
            if self._bucket_counts:
                s = sum(
                    Varint.size_varint_u64(uint32) for uint32 in self._bucket_counts
                )
                size += len(b"\x12") + s + Varint.size_varint_u32(s)
            return size

        def write_to(self, out: bytearray) -> None:
            if self.offset:
                out += b"\x08"
                Varint.write_varint_s32(out, self.offset)
            if self._bucket_counts:
                out += b"\x12"
                Varint.write_varint_u32(
                    out,
                    sum(
                        Varint.size_varint_u64(uint32) for uint32 in self._bucket_counts
                    ),
                )
                for v in self._bucket_counts:
                    Varint.write_varint_u64(out, v)


class SummaryDataPoint(MessageMarshaler):
    start_time_unix_nano: int
    time_unix_nano: int
    count: int
    sum: float

    @property
    def quantile_values(self) -> List[SummaryDataPoint.ValueAtQuantile]:
        if self._quantile_values is None:
            self._quantile_values = list()
        return self._quantile_values

    @property
    def attributes(self) -> List[KeyValue]:
        if self._attributes is None:
            self._attributes = list()
        return self._attributes

    flags: int

    def __init__(
        self,
        start_time_unix_nano: int = 0,
        time_unix_nano: int = 0,
        count: int = 0,
        sum: float = 0.0,
        quantile_values: List[SummaryDataPoint.ValueAtQuantile] = None,
        attributes: List[KeyValue] = None,
        flags: int = 0,
    ):
        self.start_time_unix_nano: int = start_time_unix_nano
        self.time_unix_nano: int = time_unix_nano
        self.count: int = count
        self.sum: float = sum
        self._quantile_values: List[SummaryDataPoint.ValueAtQuantile] = quantile_values
        self._attributes: List[KeyValue] = attributes
        self.flags: int = flags

    def calculate_size(self) -> int:
        size = 0
        if self.start_time_unix_nano:
            size += len(b"\x11") + 8
        if self.time_unix_nano:
            size += len(b"\x19") + 8
        if self.count:
            size += len(b"!") + 8
        if self.sum:
            size += len(b")") + 8
        if self._quantile_values:
            size += sum(
                message._get_size()
                + len(b"2")
                + Varint.size_varint_u32(message._get_size())
                for message in self._quantile_values
            )
        if self._attributes:
            size += sum(
                message._get_size()
                + len(b":")
                + Varint.size_varint_u32(message._get_size())
                for message in self._attributes
            )
        if self.flags:
            size += len(b"@") + Varint.size_varint_u32(self.flags)
        return size

    def write_to(self, out: bytearray) -> None:
        if self.start_time_unix_nano:
            out += b"\x11"
            out += struct.pack("<Q", self.start_time_unix_nano)
        if self.time_unix_nano:
            out += b"\x19"
            out += struct.pack("<Q", self.time_unix_nano)
        if self.count:
            out += b"!"
            out += struct.pack("<Q", self.count)
        if self.sum:
            out += b")"
            out += struct.pack("<d", self.sum)
        if self._quantile_values:
            for v in self._quantile_values:
                out += b"2"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self._attributes:
            for v in self._attributes:
                out += b":"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.flags:
            out += b"@"
            Varint.write_varint_u32(out, self.flags)

    class ValueAtQuantile(MessageMarshaler):
        quantile: float
        value: float

        def __init__(
            self,
            quantile: float = 0.0,
            value: float = 0.0,
        ):
            self.quantile: float = quantile
            self.value: float = value

        def calculate_size(self) -> int:
            size = 0
            if self.quantile:
                size += len(b"\t") + 8
            if self.value:
                size += len(b"\x11") + 8
            return size

        def write_to(self, out: bytearray) -> None:
            if self.quantile:
                out += b"\t"
                out += struct.pack("<d", self.quantile)
            if self.value:
                out += b"\x11"
                out += struct.pack("<d", self.value)


class Exemplar(MessageMarshaler):
    time_unix_nano: int
    as_double: float
    span_id: bytes
    trace_id: bytes
    as_int: int

    @property
    def filtered_attributes(self) -> List[KeyValue]:
        if self._filtered_attributes is None:
            self._filtered_attributes = list()
        return self._filtered_attributes

    def __init__(
        self,
        time_unix_nano: int = 0,
        as_double: float = None,
        span_id: bytes = b"",
        trace_id: bytes = b"",
        as_int: int = None,
        filtered_attributes: List[KeyValue] = None,
    ):
        self.time_unix_nano: int = time_unix_nano
        self.as_double: float = as_double
        self.span_id: bytes = span_id
        self.trace_id: bytes = trace_id
        self.as_int: int = as_int
        self._filtered_attributes: List[KeyValue] = filtered_attributes

    def calculate_size(self) -> int:
        size = 0
        if self.time_unix_nano:
            size += len(b"\x11") + 8
        if self.as_double is not None:
            size += len(b"\x19") + 8
        if self.span_id:
            size += (
                len(b'"')
                + Varint.size_varint_u32(len(self.span_id))
                + len(self.span_id)
            )
        if self.trace_id:
            size += (
                len(b"*")
                + Varint.size_varint_u32(len(self.trace_id))
                + len(self.trace_id)
            )
        if self.as_int is not None:
            size += len(b"1") + 8
        if self._filtered_attributes:
            size += sum(
                message._get_size()
                + len(b":")
                + Varint.size_varint_u32(message._get_size())
                for message in self._filtered_attributes
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self.time_unix_nano:
            out += b"\x11"
            out += struct.pack("<Q", self.time_unix_nano)
        if self.as_double is not None:
            out += b"\x19"
            out += struct.pack("<d", self.as_double)
        if self.span_id:
            out += b'"'
            Varint.write_varint_u32(out, len(self.span_id))
            out += self.span_id
        if self.trace_id:
            out += b"*"
            Varint.write_varint_u32(out, len(self.trace_id))
            out += self.trace_id
        if self.as_int is not None:
            out += b"1"
            out += struct.pack("<q", self.as_int)
        if self._filtered_attributes:
            for v in self._filtered_attributes:
                out += b":"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
