#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
This module is a temporary bridge from opentelemetry 1.12.0 our current
dependency, which does not have common encoder functions to the later versions
of opentelemetry, which do have common encoder functions in the
opentelemetry-exporter-otlp-proto-common package.
"""

from typing import Sequence

from opentelemetry.exporter.otlp.proto.http._log_exporter import encoder
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.sdk._logs import LogData


def _encode_logs(batch: Sequence[LogData]) -> ExportLogsServiceRequest:
    # Will no longer rely on _encode_resource_logs after we upgrade to v1.19.0 or later
    resource_logs = encoder._encode_resource_logs(batch) # pylint: disable=protected-access
    return ExportLogsServiceRequest(resource_logs=resource_logs)
