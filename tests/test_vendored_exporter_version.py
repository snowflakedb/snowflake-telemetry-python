import unittest

from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common.version import __version__ as vendored_version

from opentelemetry.sdk.version import __version__ as sdk_version
from opentelemetry.exporter.otlp.proto.common.version import __version__ as exporter_version

class TestVendoredExporterVersion(unittest.TestCase):
    def test_version(self):
        self.assertEqual(sdk_version, vendored_version, "SDK version should match vendored version")
        self.assertEqual(exporter_version, vendored_version, "Exporter version should match vendored version")
