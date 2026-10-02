> Derived-from: snowflakedb/snowflake-telemetry-python@8b2709d · generated 2026-04-08
> Regenerate when: `SpanWriter`/`MetricWriter` gain a default (non-abstract)
> implementation, `_RESERVED_ATTRS` changes, or any network/file I/O is added to `src/`

## The caller is the trust boundary, not this code

This is a library called in-process. Its only "input" is whatever arguments the
embedding Python process passes to `snowflake.telemetry.add_event()`,
`snowflake.telemetry.set_span_attribute()`, or a `logging` call that flows through a
`logging.Handler` configured with `SnowflakeLogFormatter`
(`src/snowflake/telemetry/logs/__init__.py`). The caller and the code executing this
library's functions run as the same principal, in the same process — there is no
network hop, no serialization boundary, and no authentication step inside this
repository between "whoever can execute Python here" and "whoever can call this
API." Any code that can import `snowflake.telemetry` can call every function in it
with arbitrary argument values; this repository enforces no authorization on top of
that.

## This library never transmits or persists the data it serializes

`ProtoSpanExporter._serialize_traces_data()`
(`src/snowflake/telemetry/_internal/exporter/otlp/proto/traces/__init__.py`) and
`ProtoMetricExporter._serialize_metrics_data()`
(`src/snowflake/telemetry/_internal/exporter/otlp/proto/metrics/__init__.py`) produce
`bytes` and immediately hand them to `self.span_writer.write_span(...)` /
`self.metric_writer.write_metrics(...)`. `SpanWriter.write_span` and
`MetricWriter.write_metrics` are declared with `@abc.abstractmethod` and have no
body in either class — the embedding application must subclass `SpanWriter` or
`MetricWriter` and implement the method itself before any serialized data goes
anywhere. This repository ships no such subclass (the closest thing, an
`InMemorySpanWriter`/`InMemoryMetricWriter`, exists only under `tests/`, per the
module docstrings in both files).

Combined with the absence of any socket/HTTP/file-write call anywhere in `src/`
(see `architecture.md`), a finding that assumes this repository's code sends
telemetry data to a specific network destination, an S3 bucket, or a database is
describing the *embedding application's* writer implementation — which lives
outside this repository — not code that exists here.

## The one caller-input guard this repo does enforce: reserved log attributes

`SnowflakeLogFormatter.format()` (`src/snowflake/telemetry/logs/__init__.py`) builds
its output `attributes` dict in two steps: it first sets `code.lineno`,
`code.function`, `code.filepath` from the real `LogRecord` fields, and — when an
exception is attached — `exception.type`, `exception.message`,
`exception.stacktrace`. It then iterates `record.__dict__.items()` (which includes
whatever a caller passed via `logging`'s `extra=` argument) and skips any key that
appears in `_RESERVED_ATTRS`, a frozenset that includes exactly those six
`code.*`/`exception.*` keys plus the standard `logging.LogRecord` attribute names
(`src/snowflake/telemetry/logs/__init__.py:11-42`). The effect: a caller cannot use
`extra={"code.lineno": ...}` (or any of the other reserved keys) to overwrite the
values this formatter derives from the actual call site. This is exercised by
`tests/test_snowflake_log_formatter.py#test_normal_log`, which passes
`extra={"body": 123, "code.lineno": 35}` and asserts the emitted `code.lineno` is
the real line number (21 in that test), not the caller-supplied 35, while the
non-reserved `body` key is passed through unchanged.

No other caller-supplied value (event names, span/log attribute values, metric
data points) is validated, size-capped, or filtered by this repository before being
handed to the OpenTelemetry SDK or serialized to protobuf bytes.

## `SnowflakeTraceIdGenerator`'s trace-ID generation

`SnowflakeTraceIdGenerator.generate_trace_id()`
(`src/snowflake/telemetry/trace/__init__.py`) builds a 16-byte trace ID from a
4-byte big-endian encoding of "minutes since the epoch" followed by 12 bytes from
`random.getrandbits(96)` — the stdlib's non-cryptographic PRNG, not the `secrets`
module.

## Two independent build/publish pipelines exist for this package

- `.github/workflows/python-publish.yml` runs on `release: types: [published]`
  (`:11-13`) and publishes to the public PyPI registry using
  `pypa/gh-action-pypi-publish@release/v1` (`:36`) authenticated with the
  `PYPI_API_TOKEN` repository secret (`:39`) — a stored token, not PyPI's OIDC
  "trusted publishing."
- `build.sh` and `pypi-build.sh` are, per their own header comments, "called from a
  Jenkins job called SnowflakeTelemetryPythonPackageBuilder" (`build.sh:4`,
  `pypi-build.sh:4`) rather than from any GitHub Actions workflow in this repo.
  `build.sh` additionally adds a private conda channel,
  `https://repo.anaconda.com/pkgs/snowflake/` (`build.sh:38`), before building the
  conda-format package and removes it afterward (`build.sh:56`). Neither the
  Jenkins job's configuration nor what consumes packages from that channel is
  visible from this repository.
