import google_benchmark as benchmark

from util import get_logs_data, get_metrics_data, get_traces_data

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs
from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics
from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans

from opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs as pb2_encode_logs
from opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics as pb2_encode_metrics
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans as pb2_encode_spans

"""
-----------------------------------------------------------------------------
Benchmark                                   Time             CPU   Iterations
-----------------------------------------------------------------------------
test_bm_serialize_logs_data             78590 ns        78590 ns         8893
test_bm_pb2_serialize_logs_data         96043 ns        96043 ns         7277
test_bm_serialize_metrics_data         132482 ns       132482 ns         5285
test_bm_pb2_serialize_metrics_data     163929 ns       163931 ns         4270
test_bm_serialize_traces_data          103523 ns       103524 ns         6656
test_bm_pb2_serialize_traces_data      132048 ns       132048 ns         5294
"""

def sanity_check():
    logs_data = get_logs_data()
    metrics_data = get_metrics_data()
    traces_data = get_traces_data()
    
    assert encode_logs(logs_data) == pb2_encode_logs(logs_data).SerializeToString()
    assert encode_metrics(metrics_data) == pb2_encode_metrics(metrics_data).SerializeToString()
    assert encode_spans(traces_data) == pb2_encode_spans(traces_data).SerializeToString()

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
