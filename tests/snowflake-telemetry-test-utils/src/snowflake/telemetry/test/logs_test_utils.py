#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import typing

from opentelemetry.proto.logs.v1.logs_pb2 import (
    LogsData,
)
from snowflake.telemetry._internal.exporter.otlp.proto.logs import (
    LogWriter,
)


class InMemoryLogWriter(LogWriter):
    """Implementation of :class:`.LogWriter` that stores protobufs in memory.

    This class is intended for testing purposes. It stores the deserialized
    protobuf messages in a list in memory that can be retrieved using the
    :func:`.get_finished_protos` method.
    """

    def __init__(self):
        self._protos = []

    def write_logs(self, serialized_logs: bytes) -> None:
        message = LogsData()
        message.ParseFromString(serialized_logs)
        self._protos.append(message)

    def get_finished_protos(self) -> typing.Tuple[LogsData, ...]:
        return tuple(self._protos)

    def clear(self):
        self._protos.clear()
