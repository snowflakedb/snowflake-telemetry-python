#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import typing

from opentelemetry.proto.metrics.v1.metrics_pb2 import (
    MetricsData,
)
from snowflake.telemetry._internal.exporter.otlp.proto.metrics import (
    MetricWriter,
)


class InMemoryMetricWriter(MetricWriter):
    """Implementation of :class:`.MetricWriter` that stores protobufs in
    memory.

    This class is intended for testing purposes. It stores the deserialized
    protobuf messages in a list in memory that can be retrieved using the
    :func:`.get_finished_protos` method.
    """

    def __init__(self):
        self._protos = []

    def write_metrics(self, serialized_metrics: bytes) -> None:
        message = MetricsData()
        message.ParseFromString(serialized_metrics)
        self._protos.append(message)

    def get_finished_protos(self) -> typing.Tuple[MetricsData, ...]:
        return tuple(self._protos)

    def clear(self):
        self._protos.clear()
