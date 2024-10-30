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

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._internal import (
    _encode_attributes,
)
from snowflake.telemetry._internal.opentelemetry.proto.common.v1.common import InstrumentationScope as MarshalInstrumentationScope
from snowflake.telemetry._internal.opentelemetry.proto.metrics.v1.metrics import (
    NumberDataPoint as MarshalNumberDataPoint,
    HistogramDataPoint as MarshalHistogramDataPoint,
    ExponentialHistogramDataPoint as MarshalExponentialHistogramDataPoint,
    ExponentialHistogramDataPoint_Buckets as MarshalBuckets,
    Metric as MarshalMetric,
    Gauge as MarshalGauge,
    Histogram as MarshalHistogram,
    Sum as MarshalSum,
    ExponentialHistogram as MarshalExponentialHistogram,
    ResourceMetrics as MarshalResourceMetrics,
    MetricsData as MarshalMetricsData,
    ScopeMetrics as MarshalScopeMetrics,
)
from opentelemetry.sdk.metrics.export import (
    MetricsData,
    Gauge,
    Histogram as HistogramType,
    Sum,
    ExponentialHistogram as ExponentialHistogramType,
)
from snowflake.telemetry._internal.opentelemetry.proto.resource.v1.resource import (
    Resource as MarshalResource,
)

_logger = logging.getLogger(__name__)


def encode_metrics(data: MetricsData) -> bytes:
    resource_metrics_dict = {}

    for resource_metrics in data.resource_metrics:

        resource = resource_metrics.resource

        # It is safe to assume that each entry in data.resource_metrics is
        # associated with an unique resource.
        scope_metrics_dict = {}

        resource_metrics_dict[resource] = scope_metrics_dict

        for scope_metrics in resource_metrics.scope_metrics:

            pb2_metrics = []
            pb2_metric_gauge = None
            pb2_metric_histogram = None
            pb2_metric_sum = None
            pb2_metric_exponential_histogram = None
            for metric in scope_metrics.metrics:
                if isinstance(metric.data, Gauge):
                    pb2_data_points = []
                    for data_point in metric.data.data_points:
                        as_int = None
                        as_double = None
                        if isinstance(data_point.value, int):
                            as_int = data_point.value
                        else:
                            as_double = data_point.value

                        pt = MarshalNumberDataPoint(
                            attributes=_encode_attributes(
                                data_point.attributes
                            ),
                            time_unix_nano=data_point.time_unix_nano,
                            as_int=as_int,
                            as_double=as_double,
                        )
                        pb2_data_points.append(pt)
                    
                    pb2_metric_gauge = MarshalGauge(data_points=pb2_data_points)

                elif isinstance(metric.data, HistogramType):
                    pb2_data_points = []
                    pb2_aggregation_temporality = None
                    for data_point in metric.data.data_points:
                        pt = MarshalHistogramDataPoint(
                            attributes=_encode_attributes(
                                data_point.attributes
                            ),
                            time_unix_nano=data_point.time_unix_nano,
                            start_time_unix_nano=(
                                data_point.start_time_unix_nano
                            ),
                            count=data_point.count,
                            sum=data_point.sum,
                            bucket_counts=data_point.bucket_counts,
                            explicit_bounds=data_point.explicit_bounds,
                            max=data_point.max,
                            min=data_point.min,
                        )
                        pb2_aggregation_temporality = (
                            metric.data.aggregation_temporality
                        )
                        pb2_data_points.append(pt)
                    pb2_metric_histogram = MarshalHistogram(
                        data_points=pb2_data_points, 
                        aggregation_temporality=pb2_aggregation_temporality
                    )

                elif isinstance(metric.data, Sum):
                    pb2_data_points = []
                    pb2_is_monotonic = None
                    pb2_aggregation_temporality = None
                    for data_point in metric.data.data_points:
                        as_int = None
                        as_double = None
                        if isinstance(data_point.value, int):
                            as_int = data_point.value
                        else:
                            as_double = data_point.value
                        pt = MarshalNumberDataPoint(
                            attributes=_encode_attributes(
                                data_point.attributes
                            ),
                            start_time_unix_nano=(
                                data_point.start_time_unix_nano
                            ),
                            time_unix_nano=data_point.time_unix_nano,
                            as_int=as_int,
                            as_double=as_double,
                        )
                        # note that because sum is a message type, the
                        # fields must be set individually rather than
                        # instantiating a MarshalSum and setting it once
                        pb2_aggregation_temporality = (
                            metric.data.aggregation_temporality
                        )
                        pb2_is_monotonic = metric.data.is_monotonic
                        pb2_data_points.append(pt)
                    pb2_metric_sum = MarshalSum(
                        data_points=pb2_data_points,
                        aggregation_temporality=pb2_aggregation_temporality,
                        is_monotonic=pb2_is_monotonic,
                    )

                elif isinstance(metric.data, ExponentialHistogramType):
                    pb2_data_points = []
                    pb2_aggregation_temporality = None
                    for data_point in metric.data.data_points:

                        if data_point.positive.bucket_counts:
                            positive = MarshalBuckets(
                                offset=data_point.positive.offset,
                                bucket_counts=data_point.positive.bucket_counts,
                            )
                        else:
                            positive = None

                        if data_point.negative.bucket_counts:
                            negative = MarshalBuckets(
                                offset=data_point.negative.offset,
                                bucket_counts=data_point.negative.bucket_counts,
                            )
                        else:
                            negative = None

                        pt = MarshalExponentialHistogramDataPoint(
                            attributes=_encode_attributes(
                                data_point.attributes
                            ),
                            time_unix_nano=data_point.time_unix_nano,
                            start_time_unix_nano=(
                                data_point.start_time_unix_nano
                            ),
                            count=data_point.count,
                            sum=data_point.sum,
                            scale=data_point.scale,
                            zero_count=data_point.zero_count,
                            positive=positive,
                            negative=negative,
                            flags=data_point.flags,
                            max=data_point.max,
                            min=data_point.min,
                        )
                        pb2_aggregation_temporality = (
                            metric.data.aggregation_temporality
                        )
                        pb2_data_points.append(pt)
                    
                    pb2_metric_exponential_histogram = MarshalExponentialHistogram(
                        data_points=pb2_data_points,
                        aggregation_temporality=pb2_aggregation_temporality,
                    )

                else:
                    _logger.warning(
                        "unsupported data type %s",
                        metric.data.__class__.__name__,
                    )
                    continue


                pb2_metric = MarshalMetric(
                    name=metric.name,
                    description=metric.description,
                    unit=metric.unit,
                    gauge=pb2_metric_gauge,
                    histogram=pb2_metric_histogram,
                    sum=pb2_metric_sum,
                    exponential_histogram=pb2_metric_exponential_histogram,
                )

                pb2_metrics.append(pb2_metric)
            
            
            instrumentation_scope = scope_metrics.scope

            # The SDK groups metrics in instrumentation scopes already so
            # there is no need to check for existing instrumentation scopes
            # here.
            pb2_scope_metrics = MarshalScopeMetrics(
                scope=MarshalInstrumentationScope(
                    name=instrumentation_scope.name,
                    version=instrumentation_scope.version,
                ),
                metrics=pb2_metrics,
            )

            scope_metrics_dict[instrumentation_scope] = pb2_scope_metrics

    resource_data = []
    for (
        sdk_resource,
        scope_data,
    ) in resource_metrics_dict.items():
        resource_data.append(
            MarshalResourceMetrics(
                resource=MarshalResource(
                    attributes=_encode_attributes(sdk_resource.attributes)
                ),
                scope_metrics=scope_data.values(),
                schema_url=sdk_resource.schema_url,
            )
        )
    resource_metrics = resource_data
    return bytes(MarshalMetricsData(resource_metrics=resource_metrics))