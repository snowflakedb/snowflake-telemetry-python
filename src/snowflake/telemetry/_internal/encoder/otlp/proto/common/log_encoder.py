#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

from typing import Sequence

from opentelemetry.exporter.otlp.proto.http._log_exporter import encoder
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData
from opentelemetry.sdk._logs import LogData


def _encode_logs(batch: Sequence[LogData]) -> ExportLogsServiceRequest:
    # Will no longer rely on _encode_resource_logs after we upgrade to v1.19.0 or later
    resource_logs = encoder._encode_resource_logs(batch)
    return ExportLogsServiceRequest(resource_logs=resource_logs)

def serialize_logs_data(batch: Sequence[LogData]) -> bytes:
    return LogsData(
        resource_logs=_encode_logs(batch).resource_logs
    ).SerializeToString()


__all__ = [
    "serialize_logs_data",
]
