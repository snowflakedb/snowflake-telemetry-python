"""
Test protoc code generator plugin for custom protoc message types
"""
import unittest
import tempfile
import subprocess
import os

# Import into globals() so generated code string can be compiled
from snowflake.telemetry._internal.serialize import *

class TestProtocPlugin(unittest.TestCase):
    def namespace_serialize_message(self, message_type: str, local_namespace: dict, **kwargs) -> bytes:
        assert message_type in local_namespace, f"Message type {message_type} not found in local namespace"
        return local_namespace[message_type](**kwargs).SerializeToString()

    def test_protoc_plugin(self):
        with tempfile.NamedTemporaryFile(suffix=".proto", mode="w", delete=False) as proto_file:
            # Define a simple proto file
            proto_file.write(
                """syntax = "proto3";
package opentelemetry.proto.common.v1;

message AnyValue {
  oneof value {
    string string_value = 1;
    bool bool_value = 2;
    int64 int_value = 3;
    double double_value = 4;
    ArrayValue array_value = 5;
    KeyValueList kvlist_value = 6;
    bytes bytes_value = 7;
  }
}

message ArrayValue {
  repeated AnyValue values = 1;
}

message KeyValueList {
  repeated KeyValue values = 1;
}

message KeyValue {
  string key = 1;
  AnyValue value = 2;
}

message InstrumentationScope {
  string name = 1;
  string version = 2;
  repeated KeyValue attributes = 3;
  uint32 dropped_attributes_count = 4;
}
"""
            )
            proto_file.flush()
            proto_file.close()

            proto_file_dir = os.path.dirname(proto_file.name)
            proto_file_name = os.path.basename(proto_file.name)

            os.environ["OPENTELEMETRY_PROTO_DIR"] = proto_file_dir

            # Run protoc with custom plugin to generate serialization code for messages
            result = subprocess.run([
                "python",
                "-m",
                "grpc_tools.protoc",
                "-I",
                proto_file_dir,
                "--plugin=protoc-gen-custom-plugin=scripts/plugin.py",
                f"--custom-plugin_out={tempfile.gettempdir()}",
                proto_file_name,
            ], capture_output=True)

            # Ensure protoc ran successfully
            self.assertEqual(result.returncode, 0)

            generated_code_file_dir = tempfile.gettempdir()
            generated_code_file_name = proto_file_name.replace(".proto", "_marshaler.py")
            generated_code_file = os.path.join(generated_code_file_dir, generated_code_file_name)

            # Ensure generated code file exists
            self.assertTrue(os.path.exists(generated_code_file))

            # Ensure code can be executed and serializes correctly
            with open(generated_code_file, "r") as f:
                generated_code = f.read()
                local_namespace = {}
                eval(compile(generated_code, generated_code_file, "exec"), globals(), local_namespace)

                self.assertEqual(b'\n\x04test', self.namespace_serialize_message("AnyValue", local_namespace, string_value="test"))
