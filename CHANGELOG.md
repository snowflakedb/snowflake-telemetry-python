# Release History

## 0.3.0 (2024-03-11)

* The `telemetry.add_event` function now adds an event to the current span, if any. This was a no op stub function before.
* The `telemetry.add_span_attribute` function now adds an attribute to the current span, if any. This was a no op stub function before.
* Added support for Python 3.11
* Removed support for Python 3.7
* Added `snowflake.telemetry._internal` module that wraps opentelemetry modules for use internally by Snowflake

## 0.2.0 (2023-05-01)

* Added support for Python 3.10

## 0.1.0 (2022-09-29)

* Update README and docstring to indicate this package is a stub

## 0.0.0 (2022-09-09)

* Initial release.
