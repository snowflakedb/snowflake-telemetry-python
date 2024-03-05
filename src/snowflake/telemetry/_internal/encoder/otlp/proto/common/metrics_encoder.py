#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module is a temporary bridge from opentelemetry 1.12.0 our current
dependency, which does not have common encoder functions to the later versions
of opentelemetry, which do have common encoder functions in the
opentelemetry-exporter-otlp-proto-common package.
"""

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.sdk.metrics.export import MetricsData


_exporter = OTLPMetricExporter()

def _encode_metrics(data: MetricsData) -> ExportMetricsServiceRequest:
    # Will no longer rely on _translate_data after we upgrade to v1.19.0 or later
    return _exporter._translate_data(data) # pylint: disable=protected-access
