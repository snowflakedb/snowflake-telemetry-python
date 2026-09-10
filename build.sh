#!/bin/bash -xe

# This script builds snowflake-telemetry-python for release. It is called from
# a Jenkins job called SnowflakeTelemetryPythonPackageBuilder.
#
# Prerequisites:
# - run from a pristine git checkout (this script refuses to build from a
#   workspace with modified, untracked, or ignored files; see
#   scripts/release_lib.sh)
# - PATH must contain only directories that are not writable by other users
#   (this script refuses to build with an unsafe PATH; see
#   scripts/release_lib.sh)
# - activate a conda environment
# - have conda-build installed, e.g. `conda install conda-build`
#
# Then, run this script.
#
# Note: While this script is intended to be run in the Jenkins environment to
# create official build artifacts, you can test it on your MacBook by
# installing miniconda3, then creating an environment like this:
#
# conda create -n my-conda-build-environment python=3.9 conda-build git
# conda activate my-conda-build-environment
# # cd into the snowflake-telemetry-python git root dir
# export SNOWFLAKE_TELEMETRY_DIR=$(pwd)
#
# For local test builds only, the workspace hygiene and PATH safety checks can
# be bypassed with:
# export SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE=1
# export SNOWFLAKE_TELEMETRY_ALLOW_UNSAFE_PATH=1
# Never set these in the Jenkins release job.

# Resolve the repo root with shell builtins only, so no external command runs
# via the ambient PATH before assert_secure_path has validated it.
case "${BASH_SOURCE[0]}" in
  */*) _script_dir="${BASH_SOURCE[0]%/*}" ;;
  *)   _script_dir="." ;;
esac
REPO_ROOT="$(cd "$_script_dir" && pwd)"
unset _script_dir
source "${REPO_ROOT}/scripts/release_lib.sh"

# This gate must run before anything that resolves commands through the
# ambient PATH, so release builds only use tools from directories that are
# not writable by other users.
assert_secure_path || exit 1

# Remove our own previous build output so it does not trip the hygiene gate.
rm -rf ./anaconda/dist

# Refuse to build unless the checkout is pristine (no modified, untracked, or
# ignored files), so release artifacts contain only committed sources. The
# explicit exit keeps this guard effective even if the script is invoked as
# `bash build.sh` without -e.
assert_clean_workspace "${REPO_ROOT}" || exit 1

make_conda_build () {
  # set default build number to 0, if SNOWFLAKE_TELEMETRY_BUILD_NUMBER is not set
  echo "Start building snowflake-telemetry-python package with build_number: ${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0}"
  # conda build takes GIT_HASH as environment variable and embed it into the build package name.
  # Record the full HEAD commit so the artifact can be traced back to an exact,
  # immutable revision (a short hash is ambiguous enough to collide).
  GIT_HASH=$(git -C "${REPO_ROOT}" rev-parse HEAD) SNOWFLAKE_TELEMETRY_BUILD_NUMBER=${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0} conda build ./anaconda --output-folder ./anaconda/dist
}

BUILD_CONDA_FORMAT=false
while getopts ":c" option; do
  case $option in
    c) # conda format
      BUILD_CONDA_FORMAT=true
  esac
done

# set up private channel to make opentelemetry dependencies available
conda config --add channels https://repo.anaconda.com/pkgs/snowflake/

# create a clean dist directory (previous output was removed before the
# workspace hygiene gate above)
mkdir -p ./anaconda/dist

if [ "$BUILD_CONDA_FORMAT" = true ] ; then
  # NOTE: the below is to output the build in .conda format.
  # To do so, we set conda_build.pkg_format = 2 and then
  # remove it later to go back to default behavior.
  conda config --set conda_build.pkg_format 2
  make_conda_build
  conda config --remove-key conda_build.pkg_format
else
  make_conda_build
fi

# Bind the build outputs to SHA-256 digests so downstream release steps can
# verify that what gets published is what this build produced.
write_sha256_manifest ./anaconda/dist || exit 1

# clean up the conda environment
conda config --remove channels https://repo.anaconda.com/pkgs/snowflake/
conda build purge
