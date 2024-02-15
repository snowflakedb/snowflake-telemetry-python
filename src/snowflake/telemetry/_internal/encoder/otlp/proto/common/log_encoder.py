#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

from logging import LogRecord
from typing import Sequence

from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData


def _encode_logs(batch: Sequence[LogRecord]) -> ExportLogsServiceRequest:
    # TODO fix this no-op implementation of encode_logs
    return ExportLogsServiceRequest(resource_logs=[])

def serialize_logs_data(batch: Sequence[LogRecord]) -> bytes:
    return LogsData(
        resource_logs=_encode_logs(batch).resource_logs
    ).SerializeToString()


__all__ = [
    "serialize_logs_data",
]
