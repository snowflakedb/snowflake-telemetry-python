> Derived-from: snowflakedb/snowflake-telemetry-python@8b2709d · generated 2026-04-08
> Regenerate when: a third vendoring/codegen script is added, or an existing
> `check-*.yml` workflow is removed without its script being removed too

## Pin the upstream ref in the script, and add a `check-*.yml` workflow that regenerates and diffs

This repository has two places where code is not hand-written but produced from an
upstream OpenTelemetry repository, and both follow the same pattern:

- `scripts/proto_codegen.sh` pins the source repo/tag in a shell variable
  (`PROTO_REPO_BRANCH_OR_COMMIT="v1.7.0"`, `scripts/proto_codegen.sh:15`), clones
  `open-telemetry/opentelemetry-proto` at that ref, and regenerates the marshaler
  code under `src/snowflake/telemetry/_internal/opentelemetry/proto/`.
  `.github/workflows/check-codegen.yml` runs this script from a clean checkout on
  every push/PR that touches `scripts/**` or that generated-code directory, and
  fails the build if the regeneration differs from what is committed.
- `scripts/vendor_otlp_proto_common.sh` does the same for
  `open-telemetry/opentelemetry-python` (`REPO_BRANCH_OR_COMMIT="v1.38.0"`,
  `scripts/vendor_otlp_proto_common.sh:12`), regenerating
  `src/snowflake/telemetry/_internal/opentelemetry/exporter/`.
  `.github/workflows/check-vendor.yml` is the equivalent CI check.

**When adding a third source of vendored or generated code, follow the same shape:**
pin the upstream ref in the script itself (not only in a comment), and add a
`check-*.yml` workflow, scoped by `paths:` to the script and its output directory,
that deletes the existing output, regenerates it, and fails on `git diff`.

**What this convention proves, and what it does not** — see `trust-boundaries.md`
and `threat-model.md` (INV-2, INV-3): it proves the committed code matches what the
pinned ref currently produces. It does not prove the pinned ref's content is safe,
and none of the three refs pinned in this repository's scripts or workflows
(`v1.7.0`, `v1.38.0`, and the third-party GitHub Actions used in the workflow
files under `.github/workflows/`) are pinned to an immutable commit SHA — all are tags or
tag-like refs, which a repository owner could in principle move. Do not describe
this convention as verifying the safety of the upstream source; describe it as
verifying that this repository's copy is in sync with what that source currently
contains.
