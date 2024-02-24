import logging
import unittest


from snowflake.telemetry._internal.exporter.otlp.proto.local.log_exporter import (
    ConsoleLogWriter,
    LocalLogExporter,
)
from snowflake.telemetry._internal.sdk.logs import (
    LoggerProvider,
    LoggingHandler,
)
from snowflake.telemetry._internal.sdk.logs.export import (
    SimpleLogRecordProcessor,
)


class TestSnowflakeLoggingHandler(unittest.TestCase):
    def test_snowflake_logging_handler_default_level(self):
        log_writer = ConsoleLogWriter() # Replaced with SnowflakeLogWriter in XP
        logger = logging.getLogger("default_level")
        logger.propagate = False
        logger.addHandler(SnowflakeLoggingHandler(log_writer=log_writer))

        logger.warning("Something is wrong 1")
        logger.error("Something is wrong 2")
        logger.fatal("Something is wrong 3")
        # finished_logs = exporter.get_finished_logs()
        # self.assertEqual(len(finished_logs), 1)
        # warning_log_record = finished_logs[0].log_record
        # self.assertEqual(warning_log_record.body, "Something is wrong")
        # self.assertEqual(warning_log_record.severity_text, "WARNING")
        # self.assertEqual(
        #     warning_log_record.severity_number, SeverityNumber.WARN
        # )
