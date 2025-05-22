# Snowflake Telemetry Python

[![Build and Test](https://github.com/snowflakedb/snowflake-telemetry-python/actions/workflows/build-test.yml/badge.svg)](https://github.com/snowflakedb/snowflake-telemetry-python/actions/workflows/build-test.yml)
[![License Apache-2.0](https://img.shields.io/:license-Apache%202-brightgreen.svg)](http://www.apache.org/licenses/LICENSE-2.0.txt)

## About

`snowflake-telemetry-python` is a package that supports emitting telemetry data from Python UDFs, UDTFs, and Stored Procedures.

## Getting started

To install the latest release of this package as an end user, run

```bash
VERSION="0.3.0"
curl -L "https://github.com/snowflakedb/snowflake-telemetry-python/archive/refs/tags/v${VERSION}.tar.gz" > "snowflake-telemetry-python-${VERSION}.tar.gz"
tar -xvf "snowflake-telemetry-python-${VERSION}.tar.gz"
cd "snowflake-telemetry-python-${VERSION}"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

## Development

To develop this package, run

```bash
git clone git@github.com:snowflakedb/snowflake-telemetry-python.git
cd snowflake-telemetry-python

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install . ./tests/snowflake-telemetry-test-utils
```

### Code generation

To regenerate the code under `src/snowflake/_internal/opentelemetry/proto/`, execute the script `./scripts/proto_codegen.sh`. The script expects the `src/snowflake/_internal/opentelemetry/proto/` directory to exist, and will delete all .py files in it before regerating the code.

The commit/branch/tag of [opentelemetry-proto](https://github.com/open-telemetry/opentelemetry-proto) that the code is generated from is pinned to PROTO_REPO_BRANCH_OR_COMMIT, which can be configured in the script. It is currently pinned to the same tag as [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/blob/main/scripts/proto_codegen.sh#L15).


### Release

Release to pypi is done via [Upload Python Package](https://github.com/snowflakedb/snowflake-telemetry-python/actions/workflows/python-publish.yml) workflow and it is triggered whenever a new [release](https://github.com/snowflakedb/snowflake-telemetry-python/releases) is created. Before creating a release, the PR to update versions ([example](https://github.com/snowflakedb/snowflake-telemetry-python/pull/54)) should be merged to main branch first.