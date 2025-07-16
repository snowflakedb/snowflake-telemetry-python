# Release History

## 0.7.1 (2025-07-16)

* Adds missing `scope` field to the `SnowflakeLogFormatter`.
* Set `severity_text` to `UNSPECIFIED` when it is unavailable in `SnowflakeLogFormatter`.
* Move log record attributes to nested `attributes` section in `SnowflakeLogFormatter`.

## 0.7.0 (2025-06-18)

* Adds a `SnowflakeLogFormatter` implementation which can used to emit JSON logs in a format that can be parsed by Snowflake.

## 0.6.1 (2025-05-22)

* Fix typo in CHANGELOG 

## 0.6.0 (2025-02-14)

* Upgrade OpenTelemetry Python dependencies to version 1.26.0
* Vendored in adapter code from package opentelemetry-exporter-otlp-proto-common and replaced protobuf dependency with custom vanilla python serialization

## 0.5.0 (2024-07-23)

* Set empty resource for Python OpenTelemetry config.
* Add SnowflakeTraceIdGenerator implementation.

## 0.4.0 (2024-04-22)

* Upgrade OpenTelemetry Python dependencies to version 1.23.0
* Drop the dependency on package opentelemetry-exporter-otlp and all its transitive dependencies
* Add a dependency on package opentelemetry-exporter-otlp-proto-common, a lighter weight package that brings in fewer transitive dependencies
* Remove unnecessary upper bound on setuptools dependency

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
