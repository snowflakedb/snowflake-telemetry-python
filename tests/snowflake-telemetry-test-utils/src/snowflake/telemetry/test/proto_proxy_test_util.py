import importlib
from unittest import mock
import snowflake.telemetry._internal.proto_proxy

def reload_proto_proxy(use_py):
    if use_py:
        with mock.patch("google.protobuf", side_effect=ImportError):
            importlib.reload(snowflake.telemetry._internal.proto_proxy)
        assert snowflake.telemetry._internal.proto_proxy.PROTOBUF_VERSION_MAJOR == -1
    else:
        importlib.reload(snowflake.telemetry._internal.proto_proxy)
        proto_version = int(importlib.import_module("google.protobuf").__version__[0])
        assert snowflake.telemetry._internal.proto_proxy.PROTOBUF_VERSION_MAJOR == proto_version
