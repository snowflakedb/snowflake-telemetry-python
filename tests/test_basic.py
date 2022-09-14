"""Tests for Snowflake Telemetry Python.
"""
from snowflake import telemetry


def test_version():
    """Tests that the version is correctly setup."""
    print(telemetry.__version__)


def test_basic():
    """Tests all the APIs"""
    telemetry.add_event("EventName")
    telemetry.add_event("EventName",
                        {"Attribute1": "Val1", "Attribute2": "Val2"})
    telemetry.set_span_attribute("SpanAttribute", "Val")
