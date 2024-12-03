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
test_bm_serialize_logs_data_4MB      730591536 ns    730562298 ns            1
test_bm_pb2_serialize_logs_data_4MB  702522039 ns    702490893 ns            1
test_bm_serialize_logs_data             100882 ns       100878 ns         6930
test_bm_pb2_serialize_logs_data          97112 ns        97109 ns         7195
test_bm_serialize_metrics_data          114938 ns       114934 ns         6096
test_bm_pb2_serialize_metrics_data      161849 ns       161845 ns         4324
test_bm_serialize_traces_data           123977 ns       123973 ns         5633
test_bm_pb2_serialize_traces_data       131016 ns       131011 ns         5314
"""

def sanity_check():
    logs_data = get_logs_data()
    metrics_data = get_metrics_data()
    traces_data = get_traces_data()

    assert encode_logs(logs_data).SerializeToString() == pb2_encode_logs(logs_data).SerializeToString()
    assert encode_metrics(metrics_data).SerializeToString() == pb2_encode_metrics(metrics_data).SerializeToString()
    assert encode_spans(traces_data).SerializeToString() == pb2_encode_spans(traces_data).SerializeToString()

@benchmark.register
def test_bm_serialize_logs_data_4MB(state):
    logs_data = get_logs_data_4MB()
    while state:
        encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_pb2_serialize_logs_data_4MB(state):
    logs_data = get_logs_data_4MB()
    while state:
        pb2_encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_serialize_logs_data(state):
    logs_data = get_logs_data()
    while state:
        encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_pb2_serialize_logs_data(state):
    logs_data = get_logs_data()
    while state:
        pb2_encode_logs(logs_data).SerializeToString()

@benchmark.register
def test_bm_serialize_metrics_data(state):
    metrics_data = get_metrics_data()
    while state:
        encode_metrics(metrics_data).SerializeToString()

@benchmark.register
def test_bm_pb2_serialize_metrics_data(state):
    metrics_data = get_metrics_data()
    while state:
        pb2_encode_metrics(metrics_data).SerializeToString()

@benchmark.register
def test_bm_serialize_traces_data(state):
    traces_data = get_traces_data()
    while state:
        encode_spans(traces_data).SerializeToString()

@benchmark.register
def test_bm_pb2_serialize_traces_data(state):
    traces_data = get_traces_data()
    while state:
        pb2_encode_spans(traces_data).SerializeToString()

if __name__ == "__main__":
    sanity_check()
    benchmark.main()