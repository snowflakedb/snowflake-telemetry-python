"""
Tests for Snowflake Telemetry Python.
"""
import unittest

from snowflake import telemetry
from opentelemetry.trace import get_current_span
from opentelemetry.sdk.trace import (
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from opentelemetry.trace.span import INVALID_SPAN


class TestBasic(unittest.TestCase):
    def test_version(self):
        """
        Tests that the version is correctly set up
        """
        self.assertIsNotNone(telemetry.__version__)
        self.assertIsInstance(telemetry.__version__, str)

    def test_api_without_current_span(self):
        """
        Tests that no exceptions are raised by public API methods when called without a current span
        """
        self.assertEqual(get_current_span(), INVALID_SPAN)
        telemetry.add_event("EventName1")
        telemetry.add_event("EventName2",
                            {
                                "Attribute1": "Val1",
                                "Attribute2": "Val2"
                            })
        telemetry.set_span_attribute("SpanAttribute1", "Val")

    def test_add_event(self):
        """
        Tests expected behavior when calling add_event with a valid current span
        """
        self.configure_open_telemetry()
        with self.tracer.start_as_current_span("Auto-instrumented span"):
            self.assertNotEqual(get_current_span(), INVALID_SPAN)
            telemetry.add_event("EventName1")
            get_current_span().end()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        events = spans[0].events
        self.assertEqual(1, len(events))
        self.assertEqual('EventName1', events[0].name)
        self.assertEqual(0, len(events[0].attributes))

    def test_add_event_none_name(self):
        """
        Tests expected behavior when calling add_event with a valid current span, but name == None
        """
        self.configure_open_telemetry()
        with self.tracer.start_as_current_span("Auto-instrumented span"):
            self.assertNotEqual(get_current_span(), INVALID_SPAN)
            telemetry.add_event(None)
            get_current_span().end()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        events = spans[0].events
        self.assertEqual(1, len(events))
        self.assertEqual(None, events[0].name)
        self.assertEqual(0, len(events[0].attributes))

    def test_add_event_empty_name(self):
        """
        Tests expected behavior when calling add_event with a valid current span
        """
        self.configure_open_telemetry()
        with self.tracer.start_as_current_span("Auto-instrumented span"):
            self.assertNotEqual(get_current_span(), INVALID_SPAN)
            telemetry.add_event("")
            get_current_span().end()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        events = spans[0].events
        self.assertEqual(1, len(events))
        self.assertEqual("", events[0].name)
        self.assertEqual(0, len(events[0].attributes))

    def test_add_event_with_attributes(self):
        self.configure_open_telemetry()
        with self.tracer.start_as_current_span("Auto-instrumented span"):
            self.assertNotEqual(get_current_span(), INVALID_SPAN)
            telemetry.add_event("EventName2",
                                {
                                    "some int": 42,
                                    "some str": "Val1",
                                    "some float": 3.14,
                                    "a true value": True,
                                    "a false value": False,
                                    "a none value": None,
                                })
            get_current_span().end()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        events = spans[0].events
        self.assertEqual(1, len(events))
        self.assertEqual('EventName2', events[0].name)
        attributes = events[0].attributes
        self.assertEqual(5, len(attributes))
        self.assertEqual(42, attributes["some int"])
        self.assertEqual("Val1", attributes["some str"])
        self.assertEqual(3.14, attributes["some float"])
        self.assertTrue(attributes["a true value"])
        self.assertFalse(attributes["a false value"])

    def test_set_span_attribute(self):
        self.configure_open_telemetry()
        with self.tracer.start_as_current_span("Auto-instrumented span"):
            self.assertNotEqual(get_current_span(), INVALID_SPAN)
            telemetry.set_span_attribute("some int", 42)
            telemetry.set_span_attribute("some str", "Val1")
            telemetry.set_span_attribute("some float", 3.14)
            telemetry.set_span_attribute("a true value", True)
            telemetry.set_span_attribute("a false value", False)
            telemetry.set_span_attribute("a none value", None)
            get_current_span().end()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        attributes = spans[0].attributes
        self.assertEqual(5, len(attributes))
        self.assertEqual(42, attributes["some int"])
        self.assertEqual("Val1", attributes["some str"])
        self.assertEqual(3.14, attributes["some float"])
        self.assertTrue(attributes["a true value"])
        self.assertFalse(attributes["a false value"])

    def configure_open_telemetry(self) -> None:
        self.tracer_provider = TracerProvider()
        self.tracer = self.tracer_provider.get_tracer("snowflake-trace-events")
        self.memory_exporter = InMemorySpanExporter()
        span_processor = SimpleSpanProcessor(self.memory_exporter)
        self.tracer_provider.add_span_processor(span_processor)
