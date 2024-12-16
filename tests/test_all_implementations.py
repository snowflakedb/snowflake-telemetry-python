import importlib

import snowflake.telemetry._internal.exporter.otlp.proto.logs
import snowflake.telemetry._internal.exporter.otlp.proto.traces
import snowflake.telemetry._internal.exporter.otlp.proto.metrics

import test_log_encoder
import test_trace_encoder
import test_metrics_encoder

from snowflake.telemetry.test.proto_proxy_test_util import reload_proto_proxy

class TestOTLPLogEncoderPy(test_log_encoder.TestOTLPLogEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=True)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.logs)
        importlib.reload(test_log_encoder)

class TestOTLPTraceEncoderPy(test_trace_encoder.TestOTLPTraceEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=True)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.traces)
        importlib.reload(test_trace_encoder)

class TestOTLPMetricsEncoderPy(test_metrics_encoder.TestOTLPMetricsEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=True)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.metrics)
        importlib.reload(test_metrics_encoder)

class TestOTLPLogEncoderPb(test_log_encoder.TestOTLPLogEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=False)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.logs)
        importlib.reload(test_log_encoder)

class TestOTLPTraceEncoderPb(test_trace_encoder.TestOTLPTraceEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=False)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.traces)
        importlib.reload(test_trace_encoder)

class TestOTLPMetricsEncoderPb(test_metrics_encoder.TestOTLPMetricsEncoder):
    def setUp(self):
        reload_proto_proxy(use_py=False)
        importlib.reload(snowflake.telemetry._internal.exporter.otlp.proto.metrics)
        importlib.reload(test_metrics_encoder)
