import unittest
from unittest.mock import patch

from opentelemetry import trace
from snowflake.telemetry.trace import SnowflakeTraceIdGenerator

MOCK_TIMESTAMP = 1719588243.3379807
INVALID_TRACE_ID = 0x00000000000000000000000000000000
TRACE_ID_MAX_VALUE = 2**128 - 1
SPAN_ID_MAX_VALUE = 2**64 - 1


class TestSnowflakeTraceIdGenerator(unittest.TestCase):

    def test_valid_span_id(self):
        id_generator = SnowflakeTraceIdGenerator()
        self.assertTrue(trace.INVALID_SPAN_ID < id_generator.generate_span_id() <= SPAN_ID_MAX_VALUE)
        self.assertTrue(trace.INVALID_SPAN_ID < id_generator.generate_span_id() <= SPAN_ID_MAX_VALUE)
        self.assertTrue(trace.INVALID_SPAN_ID < id_generator.generate_span_id() <= SPAN_ID_MAX_VALUE)
        self.assertTrue(trace.INVALID_SPAN_ID < id_generator.generate_span_id() <= SPAN_ID_MAX_VALUE)
        self.assertTrue(trace.INVALID_SPAN_ID < id_generator.generate_span_id() <= SPAN_ID_MAX_VALUE)

    @patch('time.time', return_value=MOCK_TIMESTAMP)
    def test_valid_snowflake_trace_id(self, mock_time):
        id_generator = SnowflakeTraceIdGenerator()
        self._verify_snowflake_trace_id(id_generator.generate_trace_id())
        self._verify_snowflake_trace_id(id_generator.generate_trace_id())
        self._verify_snowflake_trace_id(id_generator.generate_trace_id())
        self._verify_snowflake_trace_id(id_generator.generate_trace_id())
        self._verify_snowflake_trace_id(id_generator.generate_trace_id())

    def _verify_snowflake_trace_id(self, trace_id: int):
        # https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-api/src/opentelemetry/trace/span.py
        self.assertTrue(trace.INVALID_TRACE_ID < trace_id <= TRACE_ID_MAX_VALUE)

        # Get the hex format of the snowflake_trace_id and pad it to 32 characters
        # The timestamp prefix is the first 8 characters of this.
        timestamp_prefix = f'{trace_id:x}'.zfill(32)[:8]

        # the expected prefix is the timestamp (in minutes) in hex format padded to 8 characters.
        mock_timestamp_minutes = int(MOCK_TIMESTAMP) // 60
        mock_timestamp_prefix = f'{mock_timestamp_minutes:x}'.zfill(8)
        self.assertEqual(timestamp_prefix, mock_timestamp_prefix)
