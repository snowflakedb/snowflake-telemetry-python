#!/bin/bash -xe

# This script builds snowflake-telemetry-python for release. It is called from
# a Jenkins job called SnowflakeTelemetryPythonPackageBuilder.
#
# Prequisites:
# - activate a conda environment
# - have conda-build installed, e.g. `conda install conda-build`
# - have conda-verify installed, e.g. `conda install conda-verify`
#
# Then, run this script.
#
# Note: While this script is intended to be run in the Jenkins environment to
# create official build artifacts, you can test it on your MacBook by
# installing miniconda3, then creating an environment like this:
#
# conda create -n my-conda-build-environment python=3.8 conda-build git
# conda activate my-conda-build-environment
# # cd into the snowflake-telemetry-python git root dir
# export SNOWFLAKE_TELEMETRY_DIR=$(pwd)

make_conda_build () {
  # set default build number to 0, if SNOWFLAKE_TELEMETRY_BUILD_NUMBER is not set
  echo "Start building snowflake-telemetry-python package with build_number: ${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0}"
  # conda build takes GIT_HASH as environment variable and embed it into the build package name
  GIT_HASH=$(git rev-parse --short HEAD) SNOWFLAKE_TELEMETRY_BUILD_NUMBER=${SNOWFLAKE_TELEMETRY_BUILD_NUMBER:=0} conda build ./anaconda --output-folder ./anaconda/dist
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

# clean up the dist directory
rm -rf ./anaconda/dist
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

# clean up the conda environment
conda config --remove channels https://repo.anaconda.com/pkgs/snowflake/
conda build purge
