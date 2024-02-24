#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import abc
from typing import Sequence

from opentelemetry.proto.logs.v1.logs_pb2 import LogsData
from snowflake.telemetry._internal.encoder.otlp.proto.common.log_encoder import (
    serialize_logs_data
)
from snowflake.telemetry._internal.sdk.logs import LogData
from snowflake.telemetry._internal.sdk.logs.export import (
    LogExporter,
    LogExportResult,
)

# LogWriter abstract class with one abstract method that can be overwritten:
class LogWriter(abc.ABC):

    @abc.abstractmethod
    def write_logs(self, serialized_logs: bytes) -> LogExportResult:
        """quick"""


class LocalLogExporter(LogExporter):

    def __init__(self, log_writer: LogWriter):
        self.log_writer = log_writer

    def export(self, batch: Sequence[LogData]):
        print('LocalLogExporter.export called with batch size ' + str(len(batch)))
        return self.log_writer.write_logs(serialize_logs_data(batch))

    def shutdown(self):
        pass


class ConsoleLogWriter(LogWriter):
    def write_logs(self, serialized_logs: bytes) -> LogExportResult:
        message = LogsData()
        # modifies message in place, and returns number of bytes parsed
        message.ParseFromString(serialized_logs)
        print(message)
        return LogExportResult.SUCCESS
