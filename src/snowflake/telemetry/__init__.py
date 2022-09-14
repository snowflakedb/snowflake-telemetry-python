#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2022 Snowflake Computing Inc. All rights reserved.
#

# pylint: disable=unused-argument

""" Snowflake Telemetry Python
Provides a set of APIs for emitting telemetry data from Python UDF, UDTF, and
Stored Procedures.
"""

from opentelemetry.util import types

from snowflake.telemetry.version import VERSION

__version__ = ".".join(str(x) for x in VERSION if x is not None)


def add_event(
            name: str,
            attributes: types.Attributes = None,
        ) -> None:
    """Add an event to the Snowflake auto-instrumented span."""


def set_span_attribute(key: str, value: types.AttributeValue) -> None:
    """Set an attribute to the Snowflake auto-instrumented span."""
