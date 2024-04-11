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

VENV_DIR=venv_$(date +%s)
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

# install and upgrade pre-requisite packages for building snowflake-telemetry-python
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build

# clean up the dist directory
rm -rf ./dist
mkdir ./dist

# set default build number to 0, if SNOWFLAKE_TELEMETRY_BUILD_NUMBER is not set
echo "Start building snowflake-telemetry-python package with build_number: ${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0}"
SNOWFLAKE_TELEMETRY_BUILD_NUMBER=${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0} python3 -m build

deactivate
rm -rf ${VENV_DIR}
