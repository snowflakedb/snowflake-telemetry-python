#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData as PB2MetricsData
from opentelemetry.sdk.metrics.export import MetricsData


_exporter = OTLPMetricExporter()

def _encode_metrics(data: MetricsData) -> ExportMetricsServiceRequest:
    # Will no longer rely on _translate_data after we upgrade to v1.19.0 or later
    return _exporter._translate_data(data)

def serialize_metrics_data(data: MetricsData) -> bytes:
    return PB2MetricsData(
        resource_metrics=_encode_metrics(data).resource_metrics
    ).SerializeToString()


__all__ = [
    "serialize_metrics_data",
]
