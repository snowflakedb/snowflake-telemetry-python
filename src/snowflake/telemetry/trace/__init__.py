#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import time
import random

from opentelemetry import trace
from opentelemetry.sdk.trace import RandomIdGenerator

# Generator that returns
#   trace_id: the given (inherited) trace id on the first call to generate_trace_id, and a Snowflake trace_id on subsequent calls
#   span_id: a random span_id
class SnowflakeTraceIdGenerator(RandomIdGenerator):
    def generate_trace_id(self) -> int:
        trace_id = trace.INVALID_TRACE_ID
        while trace_id == trace.INVALID_TRACE_ID:
            # Number of minutes since the epoch
            timestamp_in_minutes = int(time.time()) // 60
            # Convert and pad to 4 bytes
            timestamp_bytes = timestamp_in_minutes.to_bytes(4, byteorder='big', signed=False)
            suffix_bytes = random.getrandbits(96).to_bytes(12, byteorder='big', signed=False)
            trace_id = int.from_bytes(timestamp_bytes + suffix_bytes, byteorder='big', signed=False)
        return trace_id


__all__ = [
    "SnowflakeTraceIdGenerator",
]
