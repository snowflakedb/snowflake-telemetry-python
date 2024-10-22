from util import get_logs_data

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs

from opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs as pb2_encode_logs


# Run with pytest --memray tests/benchmark_memory.py

"""
===================================================================================== MEMRAY REPORT ======================================================================================
Allocation results for benchmark/benchmark_memory.py::test_pb2_encode_logs at the high watermark

         📦 Total memory allocated: 10.0MiB
         📏 Total allocations: 7
         📊 Histogram of allocation sizes: |█ ▄▄█|
         🥇 Biggest allocating functions:
                - _encode_log:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:52 -> 6.8MiB
                - _encode_resource_logs:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:88 -> 2.3MiB
                - _encode_resource_logs:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:82 -> 865.0KiB
                - _encode_resource_logs:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:74 -> 34.4KiB
                - _encode_log:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:58 -> 646.0B


Allocation results for benchmark/benchmark_memory.py::test_encode_logs at the high watermark

         📦 Total memory allocated: 2.0MiB
         📏 Total allocations: 7
         📊 Histogram of allocation sizes: |▅  ▂█|
         🥇 Biggest allocating functions:
                - __iter__:<frozen _collections_abc>:861 -> 1.0MiB
                - serialize_message:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/_internal/serialize/__init__.py:95 -> 488.5KiB
                - serialize_bytes:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/_internal/serialize/__init__.py:75 -> 367.1KiB
                - serialize_message:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/_internal/serialize/__init__.py:95 -> 162.2KiB
                - _encode_log:/Users/jopel/workspace/snowflake-telemetry-python/.venv/lib/python3.11/site-packages/snowflake/telemetry/_internal/opentelemetry/exporter/otlp/proto/common/_internal/_log_encoder/__init__.py:56 -> 646.0B
"""

logs_data = []
for _ in range(1000):
    logs_data.extend(get_logs_data())

def test_encode_logs():
    encode_logs(logs_data)

def test_pb2_encode_logs():
    pb2_encode_logs(logs_data).SerializeToString()
