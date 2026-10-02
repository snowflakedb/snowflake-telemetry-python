> Derived-from: snowflakedb/snowflake-telemetry-python@8b2709d · generated 2026-04-08
> Regenerate when: `setup.py`'s `opentelemetry-api`/`opentelemetry-sdk` pin changes,
> either upstream ref pinned in `scripts/proto_codegen.sh` or
> `scripts/vendor_otlp_proto_common.sh` changes, a CI workflow under
> `.github/workflows/` is added or removed, or an invariant's control changes

## The system

`snowflake-telemetry-python` is a **library** (see `architecture.md`), not a service.

- **Driven by** whatever Python process imports it and calls its API. Per
  `README.md`, that is a Python UDF, UDTF, or Stored Procedure running inside
  Snowflake's Python execution environment, or any other Python program that adds
  the dependency.
- **Changed by** anyone able to merge to this repository; `.github/CODEOWNERS:1`
  designates `@snowflakedb/telemetry` as the owner of every path in the tree.
- **Trusted with** no credentials and no secrets — none are read, held, or
  transmitted anywhere in `src/`. What it is trusted with is *correctness of
  serialization*: every process that calls its API, or wires up
  `SnowflakeTraceIdGenerator` / `ProtoSpanExporter` / `ProtoMetricExporter`, relies
  on it to produce well-formed OTLP protobuf bytes and to hand them only to the
  writer the embedding application supplied (`trust-boundaries.md`) — never to an
  implicit destination of its own choosing. Because the package is published to the
  public PyPI registry and, via a separate Jenkins-triggered build, to a private
  Snowflake-operated conda channel (`trust-boundaries.md`, "Two independent
  build/publish pipelines"), a change that broke either property would ship to every
  process that installs the package from either channel.
- **Reads** nothing beyond its own Python-level function arguments and, at
  maintainer-invoked dev time only, two upstream OpenTelemetry git repositories
  cloned by `scripts/proto_codegen.sh` and `scripts/vendor_otlp_proto_common.sh` (see
  below). It holds no runtime configuration, no credentials, and no per-tenant state.

## Systems and trust boundaries

| System | Role here | Crosses the boundary | Trusted for |
|---|---|---|---|
| `opentelemetry-api` / `opentelemetry-sdk` (PyPI, pinned `==1.38.0` in `setup.py`) | runtime dependency this package extends (`get_current_span`, `RandomIdGenerator`, `SpanExporter`, `MetricExporter`) | installed into, and imported by, every process using this package | that the pinned version behaves as documented — a defect or a compromised release at that exact version would run in every embedding process |
| `open-telemetry/opentelemetry-proto` (git, tag `v1.7.0` pinned at `scripts/proto_codegen.sh:15`) | schema source for the generated marshaler code under `_internal/opentelemetry/proto/` | cloned by a maintainer running `scripts/proto_codegen.sh`; never fetched at package-install or runtime | that the content at the pinned tag, when regenerated, is what CI (`.github/workflows/check-codegen.yml`) sees committed to this repo |
| `open-telemetry/opentelemetry-python` (git, tag `v1.38.0` pinned at `scripts/vendor_otlp_proto_common.sh:12`) | source of the vendored encoder code under `_internal/opentelemetry/exporter/otlp/proto/common/` | cloned by a maintainer running `scripts/vendor_otlp_proto_common.sh`; never fetched at package-install or runtime | that the content at the pinned tag, when regenerated, is what CI (`.github/workflows/check-vendor.yml`) sees committed to this repo |
| GitHub Actions (workflow files under `.github/workflows/`) + third-party actions (`actions/checkout@v3/v4`, `actions/setup-python@v3`, `pypa/gh-action-pypi-publish@release/v1`) | builds, tests, and (on `release: published`) publishes this package | source in, package artifact out; `PYPI_API_TOKEN` secret out to the publish step only | that only this repository's reviewed source is built, and that `PYPI_API_TOKEN` is used by, and visible to, no step other than `python-publish.yml`'s publish step |
| PyPI (public registry) | public distribution channel for the package built by `python-publish.yml` | release artifact out | serving exactly the artifact this repo's workflow uploaded, unaltered, to every `pip install snowflake-telemetry-python` |
| Jenkins job "SnowflakeTelemetryPythonPackageBuilder" + `repo.anaconda.com/pkgs/snowflake/` conda channel (`build.sh:4`, `build.sh:38`) | second, non-GitHub-Actions build/publish path, producing a conda package | source in (checked out by Jenkins, not visible from this repo), package artifact out to the private channel | building the published conda package only from this repository's own reviewed source, the same way `python-publish.yml` does for the PyPI artifact |
| The embedding application's `SpanWriter`/`MetricWriter` subclass | sole consumer of the OTLP protobuf bytes this repo's exporters produce | serialized bytes out, in-process | not silently discarding, corrupting, or misrouting the telemetry data this library hands it |

## Invariants

| ID | Invariant | Control | Status |
|---|---|---|---|
| INV-1 | A caller-supplied `logging` `extra=` value cannot overwrite the `code.lineno`, `code.function`, `code.filepath`, `exception.type`, `exception.message`, or `exception.stacktrace` attributes `SnowflakeLogFormatter` derives from the actual call site | `src/snowflake/telemetry/logs/__init__.py` (`_RESERVED_ATTRS`, `SnowflakeLogFormatter.format`) — mechanism detailed in `trust-boundaries.md` | Holding (`tests/test_snowflake_log_formatter.py#test_normal_log`) |
| INV-2 | The vendored encoder code under `_internal/opentelemetry/exporter/otlp/proto/common/` matches what a fresh regeneration from the pinned `opentelemetry-python` tag (`scripts/vendor_otlp_proto_common.sh:12`) produces | `.github/workflows/check-vendor.yml` (regenerates from scratch and fails on `git diff`) | Holding — covers only "the committed code matches the pinned tag's current content", not "that tag's content is safe"; see the systems-table row above and the gap this leaves open |
| INV-3 | The generated marshaler code under `_internal/opentelemetry/proto/` matches what a fresh regeneration from the pinned `opentelemetry-proto` tag (`scripts/proto_codegen.sh:15`) produces | `.github/workflows/check-codegen.yml` (regenerates from scratch and fails on `git diff`) | Holding — same partial-coverage caveat as INV-2 |
| INV-4 | `PYPI_API_TOKEN` is used only inside the publish step of `.github/workflows/python-publish.yml`, and that workflow runs only when a GitHub release is published | `.github/workflows/python-publish.yml` (trigger `release: types: [published]` at `:11-13`; token read only at `:39`, inside the `pypa/gh-action-pypi-publish` step at `:36`) | Holding |
