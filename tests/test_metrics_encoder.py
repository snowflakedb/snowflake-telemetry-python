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

# pylint: disable=protected-access
import unittest

from snowflake.telemetry._internal.encoder.otlp.proto.common.metrics_encoder import (
    _encode_metrics,
)
from snowflake.telemetry._internal.exporter.otlp.proto.metrics import (
    ProtoMetricExporter,
)
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
)
from opentelemetry.proto.common.v1.common_pb2 import (
    AnyValue,
    InstrumentationScope,
    KeyValue,
)
from opentelemetry.proto.metrics.v1 import metrics_pb2 as pb2
from opentelemetry.proto.resource.v1.resource_pb2 import (
    Resource as OTLPResource,
)
from opentelemetry.sdk.metrics.export import AggregationTemporality
from opentelemetry.sdk.metrics.export import Histogram as HistogramType
from opentelemetry.sdk.metrics.export import (
    HistogramDataPoint,
    Metric,
    MetricsData,
    ResourceMetrics,
    ScopeMetrics,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import (
    InstrumentationScope as SDKInstrumentationScope,
)
from snowflake.telemetry.test.metrictestutil import _generate_gauge, _generate_sum


class TestOTLPMetricsEncoder(unittest.TestCase):
    histogram = Metric(
        name="histogram",
        description="foo",
        unit="s",
        data=HistogramType(
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

    def test_encode_sum_int(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[_generate_sum("sum_int", 33)],
                            schema_url="instrumentation_scope_schema_url",
                        )
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="sum_int",
                                    unit="s",
                                    description="foo",
                                    sum=pb2.Sum(
                                        data_points=[
                                            pb2.NumberDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946015139533244,
                                                time_unix_nano=1641946016139533244,
                                                as_int=33,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.CUMULATIVE,
                                        is_monotonic=True,
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))

    def test_encode_sum_double(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[_generate_sum("sum_double", 2.98)],
                            schema_url="instrumentation_scope_schema_url",
                        )
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="sum_double",
                                    unit="s",
                                    description="foo",
                                    sum=pb2.Sum(
                                        data_points=[
                                            pb2.NumberDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946015139533244,
                                                time_unix_nano=1641946016139533244,
                                                as_double=2.98,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.CUMULATIVE,
                                        is_monotonic=True,
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))

    def test_encode_gauge_int(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[_generate_gauge("gauge_int", 9000)],
                            schema_url="instrumentation_scope_schema_url",
                        )
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="gauge_int",
                                    unit="s",
                                    description="foo",
                                    gauge=pb2.Gauge(
                                        data_points=[
                                            pb2.NumberDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                time_unix_nano=1641946016139533244,
                                                as_int=9000,
                                            )
                                        ],
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))

    def test_encode_gauge_double(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[_generate_gauge("gauge_double", 52.028)],
                            schema_url="instrumentation_scope_schema_url",
                        )
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="gauge_double",
                                    unit="s",
                                    description="foo",
                                    gauge=pb2.Gauge(
                                        data_points=[
                                            pb2.NumberDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                time_unix_nano=1641946016139533244,
                                                as_double=52.028,
                                            )
                                        ],
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))

    def test_encode_histogram(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[self.histogram],
                            schema_url="instrumentation_scope_schema_url",
                        )
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="histogram",
                                    unit="s",
                                    description="foo",
                                    histogram=pb2.Histogram(
                                        data_points=[
                                            pb2.HistogramDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946016139533244,
                                                time_unix_nano=1641946016139533244,
                                                count=5,
                                                sum=67,
                                                bucket_counts=[1, 4],
                                                explicit_bounds=[10.0, 20.0],
                                                exemplars=[],
                                                max=18.0,
                                                min=8.0,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.DELTA,
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))

    def test_encode_multiple_scope_histogram(self):
        metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(
                        attributes={"a": 1, "b": False},
                        schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="first_name",
                                version="first_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[self.histogram, self.histogram],
                            schema_url="instrumentation_scope_schema_url",
                        ),
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="second_name",
                                version="second_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[self.histogram],
                            schema_url="instrumentation_scope_schema_url",
                        ),
                        ScopeMetrics(
                            scope=SDKInstrumentationScope(
                                name="third_name",
                                version="third_version",
                                schema_url="insrumentation_scope_schema_url",
                            ),
                            metrics=[self.histogram],
                            schema_url="instrumentation_scope_schema_url",
                        ),
                    ],
                    schema_url="resource_schema_url",
                )
            ]
        )
        expected = ExportMetricsServiceRequest(
            resource_metrics=[
                pb2.ResourceMetrics(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_metrics=[
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first_name", version="first_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="histogram",
                                    unit="s",
                                    description="foo",
                                    histogram=pb2.Histogram(
                                        data_points=[
                                            pb2.HistogramDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946016139533244,
                                                time_unix_nano=1641946016139533244,
                                                count=5,
                                                sum=67,
                                                bucket_counts=[1, 4],
                                                explicit_bounds=[10.0, 20.0],
                                                exemplars=[],
                                                max=18.0,
                                                min=8.0,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.DELTA,
                                    ),
                                ),
                                pb2.Metric(
                                    name="histogram",
                                    unit="s",
                                    description="foo",
                                    histogram=pb2.Histogram(
                                        data_points=[
                                            pb2.HistogramDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946016139533244,
                                                time_unix_nano=1641946016139533244,
                                                count=5,
                                                sum=67,
                                                bucket_counts=[1, 4],
                                                explicit_bounds=[10.0, 20.0],
                                                exemplars=[],
                                                max=18.0,
                                                min=8.0,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.DELTA,
                                    ),
                                ),
                            ],
                        ),
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="second_name", version="second_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="histogram",
                                    unit="s",
                                    description="foo",
                                    histogram=pb2.Histogram(
                                        data_points=[
                                            pb2.HistogramDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946016139533244,
                                                time_unix_nano=1641946016139533244,
                                                count=5,
                                                sum=67,
                                                bucket_counts=[1, 4],
                                                explicit_bounds=[10.0, 20.0],
                                                exemplars=[],
                                                max=18.0,
                                                min=8.0,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.DELTA,
                                    ),
                                )
                            ],
                        ),
                        pb2.ScopeMetrics(
                            scope=InstrumentationScope(
                                name="third_name", version="third_version"
                            ),
                            metrics=[
                                pb2.Metric(
                                    name="histogram",
                                    unit="s",
                                    description="foo",
                                    histogram=pb2.Histogram(
                                        data_points=[
                                            pb2.HistogramDataPoint(
                                                attributes=[
                                                    KeyValue(
                                                        key="a",
                                                        value=AnyValue(
                                                            int_value=1
                                                        ),
                                                    ),
                                                    KeyValue(
                                                        key="b",
                                                        value=AnyValue(
                                                            bool_value=True
                                                        ),
                                                    ),
                                                ],
                                                start_time_unix_nano=1641946016139533244,
                                                time_unix_nano=1641946016139533244,
                                                count=5,
                                                sum=67,
                                                bucket_counts=[1, 4],
                                                explicit_bounds=[10.0, 20.0],
                                                exemplars=[],
                                                max=18.0,
                                                min=8.0,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.DELTA,
                                    ),
                                )
                            ],
                        ),
                    ],
                )
            ]
        )
        actual = _encode_metrics(metrics_data)
        self.assertEqual(expected, actual)
        self.assertEqual(pb2.MetricsData(resource_metrics=actual.resource_metrics).SerializeToString(),
                         ProtoMetricExporter._serialize_metrics_data(metrics_data))
