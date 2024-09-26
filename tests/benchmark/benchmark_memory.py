import unittest
from typing import Sequence

from snowflake.telemetry._internal.exporter.otlp.proto.logs import encode_logs

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk._logs import LogData, LogRecord

from opentelemetry.trace import TraceFlags

"""
v0.5.0

📦 Total memory allocated: 19.9KiB
📏 Total allocations: 19
📊 Histogram of allocation sizes: |█▁▂ ▁|
🥇 Biggest allocating functions:
    - _encode_log:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:52 -> 6.4KiB
    - _encode_resource_logs:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:88 -> 5.7KiB
    - _encode_resource_logs:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:82 -> 3.5KiB
    - __setitem__:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/attributes/__init__.py:173 -> 804.0B

"""


"""
v0.6.0.dev

📦 Total memory allocated: 6.8KiB
📏 Total allocations: 18
📊 Histogram of allocation sizes: |█  ▄ |
🥇 Biggest allocating functions:
    - __bytes__:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/serialize/__init__.py:23 -> 1.4KiB
    - __setitem__:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/attributes/__init__.py:173 -> 804.0B
    - serialize_bytes:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/serialize/__init__.py:86 -> 774.0B
    - serialize_message:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/serialize/__init__.py:103 -> 690.0B
"""

# Run with pytest --memray tests/benchmark_memory.py
def test_serialize_logs():
    logs_data = get_logs_data()
    bytes(encode_logs(logs_data))

def get_logs_data() -> Sequence[LogData]:
    log1 = LogData(
        log_record=LogRecord(
            timestamp=1644650195189786880,
            observed_timestamp=1644660000000000000,
            trace_id=89564621134313219400156819398935297684,
            span_id=1312458408527513268,
            trace_flags=TraceFlags(0x01),
            severity_text="WARN",
            severity_number=SeverityNumber.WARN,
            body="Do not go gentle into that good night. Rage, rage against the dying of the light",
            resource=Resource(
                {"first_resource": "value"},
                "resource_schema_url",
            ),
            attributes={"a": 1, "b": "c"},
        ),
        instrumentation_scope=InstrumentationScope(
            "first_name", "first_version"
        ),
    )

    log2 = LogData(
        log_record=LogRecord(
            timestamp=1644650249738562048,
            observed_timestamp=1644660000000000000,
            trace_id=0,
            span_id=0,
            trace_flags=TraceFlags.DEFAULT,
            severity_text="WARN",
            severity_number=SeverityNumber.WARN,
            body="Cooper, this is no time for caution!",
            resource=Resource({"second_resource": "CASE"}),
            attributes={},
        ),
        instrumentation_scope=InstrumentationScope(
            "second_name", "second_version"
        ),
    )

    log3 = LogData(
        log_record=LogRecord(
            timestamp=1644650427658989056,
            observed_timestamp=1644660000000000000,
            trace_id=271615924622795969659406376515024083555,
            span_id=4242561578944770265,
            trace_flags=TraceFlags(0x01),
            severity_text="DEBUG",
            severity_number=SeverityNumber.DEBUG,
            body="To our galaxy",
            resource=Resource({"second_resource": "CASE"}),
            attributes={"a": 1, "b": "c"},
        ),
        instrumentation_scope=None,
    )

    log4 = LogData(
        log_record=LogRecord(
            timestamp=1644650584292683008,
            observed_timestamp=1644660000000000000,
            trace_id=212592107417388365804938480559624925555,
            span_id=6077757853989569223,
            trace_flags=TraceFlags(0x01),
            severity_text="INFO",
            severity_number=SeverityNumber.INFO,
            body="Love is the one thing that transcends time and space",
            resource=Resource(
                {"first_resource": "value"},
                "resource_schema_url",
            ),
            attributes={"filename": "model.py", "func_name": "run_method"},
        ),
        instrumentation_scope=InstrumentationScope(
            "another_name", "another_version"
        ),
    )

    return [log1, log2, log3, log4]
