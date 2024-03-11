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

To develop this package, run

```bash
git clone git@github.com:snowflakedb/snowflake-telemetry-python.git
cd snowflake-telemetry-python

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install . ./tests/snowflake-telemetry-test-utils
```
