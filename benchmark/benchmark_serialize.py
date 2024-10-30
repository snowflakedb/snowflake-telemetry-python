import google_benchmark as benchmark

from util import get_logs_data, get_metrics_data, get_traces_data, get_logs_data_4MB

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs
from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics
from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans

from opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs as pb2_encode_logs
from opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics as pb2_encode_metrics
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans as pb2_encode_spans

"""
------------------------------------------------------------------------------
Benchmark                                    Time             CPU   Iterations
------------------------------------------------------------------------------
test_bm_serialize_logs_data_4MB      218404625 ns    218404667 ns            3
test_bm_pb2_serialize_logs_data_4MB  279917764 ns    279916000 ns            3
test_bm_serialize_logs_data              35747 ns        35747 ns        19741
test_bm_pb2_serialize_logs_data          41652 ns        41651 ns        16939
test_bm_serialize_metrics_data           59798 ns        59798 ns        11593
test_bm_pb2_serialize_metrics_data       70521 ns        70521 ns         9815
test_bm_serialize_traces_data            47156 ns        47156 ns        14807
test_bm_pb2_serialize_traces_data        59690 ns        59690 ns        11766
"""

def sanity_check():
    logs_data = get_logs_data()
    metrics_data = get_metrics_data()
    traces_data = get_traces_data()

    assert encode_logs(logs_data) == pb2_encode_logs(logs_data).SerializeToString()
    assert encode_metrics(metrics_data) == pb2_encode_metrics(metrics_data).SerializeToString()
    assert encode_spans(traces_data) == pb2_encode_spans(traces_data).SerializeToString()

@benchmark.register
def test_bm_serialize_logs_data_4MB(state):
    logs_data = get_logs_data_4MB()
    while state:
        encode_logs(logs_data)

@benchmark.register
def test_bm_pb2_serialize_logs_data_4MB(state):
    logs_data = get_logs_data_4MB()
    while state:
        pb2_encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_serialize_logs_data(state):
    logs_data = get_logs_data()
    while state:
        encode_logs(logs_data)

@benchmark.register
def test_bm_pb2_serialize_logs_data(state):
    logs_data = get_logs_data()
    while state:
        pb2_encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_serialize_metrics_data(state):
    metrics_data = get_metrics_data()
    while state:
        encode_metrics(metrics_data)

@benchmark.register
def test_bm_pb2_serialize_metrics_data(state):
    metrics_data = get_metrics_data()
    while state:
        pb2_encode_metrics(metrics_data).SerializeToString()

@benchmark.register
def test_bm_serialize_traces_data(state):
    traces_data = get_traces_data()
    while state:
        encode_spans(traces_data)

@benchmark.register
def test_bm_pb2_serialize_traces_data(state):
    traces_data = get_traces_data()
    while state:
        pb2_encode_spans(traces_data).SerializeToString()

if __name__ == "__main__":
    sanity_check()
    benchmark.main()
