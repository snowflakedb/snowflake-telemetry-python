#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import abc
import enum

from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricExporter,
    MetricsData
)
from snowflake.telemetry._internal.encoder.otlp.proto.common.metrics_encoder import (
    serialize_metrics_data
)


class MetricWriterResult(enum.Enum):
    SUCCESS = 0
    FAILURE = 1


# MetricsWriter abstract class with one abstract method that can be overwritten:
class MetricWriter(abc.ABC):

    @abc.abstractmethod
    def write_metrics(self, serialized_metrics: bytes) -> MetricWriterResult:
        """quick"""


class ProtoMetricExporter(MetricExporter):
    def __init__(self, metric_writer: MetricWriter):
        self.metric_writer = metric_writer
    
    def export(self, data: MetricsData) -> "MetricExportResult":
        result = self.metric_writer.write_metrics(serialize_metrics_data(data))
        if result == MetricWriterResult.FAILURE:
            return MetricExportResult.FAILURE
        return MetricExportResult.SUCCESS


    def force_flush(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass


__all__ = [
    "MetricWriter",
    "MetricWriterResult",
    "ProtoMetricExporter",
]
