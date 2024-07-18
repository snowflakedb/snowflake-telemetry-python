#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

"""
Snowflake Telemetry Python

Provides a set of APIs for emitting telemetry data from Python UDF, UDTF, and
Stored Procedures.
"""

from opentelemetry.trace import get_current_span
from opentelemetry.util import types

from snowflake.telemetry.version import VERSION

__version__ = VERSION


def add_event(
        name: str,
        attributes: types.Attributes = None,
    ) -> None:
    """
    Add an event name and associated attributes to the current span.
    """
    get_current_span().add_event(name, attributes)


def set_span_attribute(
        key: str,
        value: types.AttributeValue
    ) -> None:
    """
    Set an attribute key, value pair on the current span.
    """
    get_current_span().set_attribute(key, value)
