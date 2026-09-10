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
#
# For local test builds only, the workspace hygiene check can be bypassed with:
# export SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE=1
# Never set this in the Jenkins release job.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${REPO_ROOT}/scripts/release_lib.sh"

# Remove our own previous build outputs so they do not trip the hygiene gate.
rm -rf ./dist ./build venv_* src/*.egg-info

# Refuse to build unless the checkout is pristine (no modified, untracked, or
# ignored files), so release artifacts contain only committed sources. The
# explicit exit keeps this guard effective even if the script is invoked as
# `bash pypi-build.sh` without -e.
assert_clean_workspace "${REPO_ROOT}" || exit 1

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

# Bind the build outputs to SHA-256 digests so downstream release steps can
# verify that what gets published is what this build produced.
write_sha256_manifest ./dist || exit 1

deactivate
rm -rf ${VENV_DIR}
