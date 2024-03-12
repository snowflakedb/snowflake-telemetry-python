#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module allows the user to write metrics serialized as protobuf messages to
the preferred location by implementing the write_metrics() abstract method. The
only classes that should be accessed outside of this module are:

- MetricWriter
- ProtoMetricExporter

Please see the class documentation for those classes to learn more.
"""

import abc
from typing import Dict

import opentelemetry
from opentelemetry.exporter.otlp.proto.common.metrics_encoder import (
    encode_metrics,
)
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData as PB2MetricsData
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricExportResult,
    MetricExporter,
    MetricsData,
)


# pylint: disable=too-few-public-methods
class MetricWriter(abc.ABC):
    """
    MetricWriter abstract base class with one abstract method that must be
    implemented by the user.
    """
    @abc.abstractmethod
    def write_metrics(self, serialized_metrics: bytes) -> None:
        """
        Implement this method to write the serialized protobuf message to your
        preferred location. For an example implementation, see
        InMemoryMetricWriter in the tests folder.
        """


class ProtoMetricExporter(MetricExporter):
    """
    Implementation of the MetricExporter interface for exporting metrics.

    This implementation writes serialized
    opentelemetry.proto.metrics.v1.metrics_pb2.MetricsData protobuf messages
    according to the implementation you provide to the MetricWriter abstract
    base class above.
    """
    def __init__(
            self,
            metric_writer: MetricWriter,
            preferred_temporality: Dict[type, AggregationTemporality] = None,
            preferred_aggregation: Dict[
                type, "opentelemetry.sdk.metrics.view.Aggregation"
            ] = None
    ) -> None:
        super().__init__(preferred_temporality, preferred_aggregation)
        self.metric_writer = metric_writer

    def export(
            self,
            metrics_data: MetricsData,
            timeout_millis: float = 10_000,
            **kwargs
    ) -> MetricExportResult:
        try:
            self.metric_writer.write_metrics(
                ProtoMetricExporter._serialize_metrics_data(metrics_data)
            )
            return MetricExportResult.SUCCESS
        except Exception:
            return MetricExportResult.FAILURE

    @staticmethod
    def _serialize_metrics_data(data: MetricsData) -> bytes:
        # pylint gets confused by protobuf-generated code, that's why we must
        # disable the no-member check below.
        return PB2MetricsData(
            resource_metrics=encode_metrics(data).resource_metrics # pylint: disable=no-member
        ).SerializeToString()

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        return True

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        pass


__all__ = [
    "MetricWriter",
    "ProtoMetricExporter",
]
