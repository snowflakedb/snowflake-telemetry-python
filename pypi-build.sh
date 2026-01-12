#!/bin/bash -xe

# This script builds snowflake-telemetry-python for release. It is called from
# a Jenkins job called SnowflakeTelemetryPythonPackageBuilder.
#
# Prequisites:
# - activate a clean virtual environment with
#     python3 -m venv .venv
#     source .venv/bin/activate
#
# Then, run this script.
#
# Note: While this script is intended to be run in the Jenkins environment to
# create official build artifacts, you can test it on your MacBook by
# using its built-in python3, then creating an environment like this:
#
# python3 -m venv .venv
# source .venv/bin/activate
# # cd into the snowflake-telemetry-python git root dir
# export SNOWFLAKE_TELEMETRY_DIR=$(pwd)

PYTHON_VERSIONS=("3.9" "3.10" "3.11" "3.12" "3.13")

# clean up the dist directory
rm -rf ./dist
mkdir ./dist

# set default build number to 0, if SNOWFLAKE_TELEMETRY_BUILD_NUMBER is not set
echo "Start building snowflake-telemetry-python package with build_number: ${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0}"

for VERSION in "${PYTHON_VERSIONS[@]}"; do
    PYTHON="python${VERSION}"

    echo "Building wheel for Python $VERSION"

    VENV_DIR=venv_${VERSION}_$(date +%s)
    $PYTHON -m venv ${VENV_DIR}
    source ${VENV_DIR}/bin/activate

    python -m pip install --upgrade pip build wheel

    # Clear and recompile .pyc for this Python version only
    find src/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    python -m compileall src/

    # Build wheel - setup.py automatically tags with cpXX-none-any
    SNOWFLAKE_TELEMETRY_BUILD_NUMBER=${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0} python -m build --wheel

    deactivate
    rm -rf ${VENV_DIR}
done

# Build source distribution once using any available Python
VENV_DIR=venv_sdist_$(date +%s)
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate
python -m pip install --upgrade pip build
SNOWFLAKE_TELEMETRY_BUILD_NUMBER=${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0} python -m build --sdist
deactivate
rm -rf ${VENV_DIR}
