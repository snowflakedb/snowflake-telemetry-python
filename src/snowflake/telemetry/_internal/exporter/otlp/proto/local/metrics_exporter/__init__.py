#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import abc

from snowflake.telemetry._internal.encoder.otlp.proto.common.metrics_encoder import (
    serialize_metrics_data
)
from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricExporter,
    MetricsData
)


# MetricsWriter abstract class with one abstract method that can be overwritten:
class MetricWriter(abc.ABC):

    @abc.abstractmethod
    def write_metrics(self, serialized_metrics: bytes) -> MetricExportResult:
        """quick"""


class LocalMetricExporter(MetricExporter):
    def __init__(self, metric_writer: MetricWriter):
        self.metric_writer = metric_writer
    
    def export(self, data: MetricsData) -> "MetricExportResult":
        return self.metric_writer.write_metrics(serialize_metrics_data(data))

    def force_flush(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
