#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

# pylint: disable=unused-argument

""" Snowflake Telemetry Python
Provides a set of APIs for emitting telemetry data from Python UDF, UDTF, and
Stored Procedures.
"""

from opentelemetry.util.types import (
    AttributeValue,
    Attributes,
)

from snowflake.telemetry.version import VERSION

__version__ = VERSION


def add_event(
            name: str,
            attributes: Attributes = None,
        ) -> None:
    """Add an event to the Snowflake auto-instrumented span.

    This is a stub for the full functionality when running in Snowflake.
    """


def set_span_attribute(key: str, value: AttributeValue) -> None:
    """Set an attribute to the Snowflake auto-instrumented span.

    This is a stub for the full functionality when running in Snowflake.
    """
