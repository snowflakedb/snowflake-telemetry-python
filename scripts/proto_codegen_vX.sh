#!/bin/bash
#
# Regenerate python code from OTLP protos in
# https://github.com/open-telemetry/opentelemetry-proto
#
# To use, update PROTO_REPO_BRANCH_OR_COMMIT variable below to a commit hash or
# tag in opentelemtry-proto repo that you want to build off of. Then, just run
# this script to update the proto files. Commit the changes as well as any
# fixes needed in the OTLP exporter.
#
# Optional envars:
#   PROTO_REPO_DIR - the path to an existing checkout of the opentelemetry-proto repo

# Pinned commit/branch/tag for the current version used in opentelemetry-proto python package.
PROTO_REPO_BRANCH_OR_COMMIT="v1.2.0"

set -e

PB_VERSION_MAJOR=${1:-"3"}
PROTO_REPO_DIR=${PROTO_REPO_DIR:-"/tmp/opentelemetry-proto"}
# root of opentelemetry-python repo
repo_root="$(git rev-parse --show-toplevel)"
venv_dir="/tmp/proto_codegen_venv"

# run on exit even if crash
cleanup() {
    echo "Deleting $venv_dir"
    rm -rf $venv_dir
}
trap cleanup EXIT

echo "Creating temporary virtualenv at $venv_dir using $(python3 --version)"
python3.9 -m venv $venv_dir
source $venv_dir/bin/activate
pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install \
    -c $repo_root/scripts/gen-requirements-v$PB_VERSION_MAJOR.txt \
    grpcio-tools mypy-protobuf

echo 'python -m grpc_tools.protoc --version'
python -m grpc_tools.protoc --version

# Clone the proto repo if it doesn't exist
if [ ! -d "$PROTO_REPO_DIR" ]; then
    git clone https://github.com/open-telemetry/opentelemetry-proto.git $PROTO_REPO_DIR
fi

# Pull in changes and switch to requested branch
(
    cd $PROTO_REPO_DIR
    git fetch --all
    git checkout $PROTO_REPO_BRANCH_OR_COMMIT
    # pull if PROTO_REPO_BRANCH_OR_COMMIT is not a detached head
    git symbolic-ref -q HEAD && git pull --ff-only || true
)

cd $repo_root/src/snowflake/telemetry/_internal

# clean up old generated code
mkdir -p proto_impl/v$PB_VERSION_MAJOR/opentelemetry/proto
find proto_impl/v$PB_VERSION_MAJOR/opentelemetry/proto/ -regex ".*_pb2\.py" -exec rm {} +
find proto_impl/v$PB_VERSION_MAJOR/opentelemetry/proto/ -regex ".*_pb2\.pyi" -exec rm {} +

# generate proto code for all protos
all_protos=$(find $PROTO_REPO_DIR/ -iname "*.proto")
python -m grpc_tools.protoc \
    -I $PROTO_REPO_DIR \
    --python_out=./proto_impl/v$PB_VERSION_MAJOR \
    --mypy_out=./proto_impl/v$PB_VERSION_MAJOR \
    $all_protos

# since we do not have the generated files in the base directory
# we need to use sed to update the imports

# If MacOS need '' after -i
# Detect the OS (macOS or Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD="sed -i ''"
else
  SED_CMD="sed -i"
fi

find proto_impl/v$PB_VERSION_MAJOR -type f \( -name "*.py" -o -name "*.pyi" \) -exec $SED_CMD 's/^import \([^ ]*\)_pb2 as \([^ ]*\)$/import snowflake.telemetry._internal.proto_impl.v'"$PB_VERSION_MAJOR"'.\1_pb2 as \2/' {} +
find proto_impl/v$PB_VERSION_MAJOR -type f \( -name "*.py" -o -name "*.pyi" \) -exec $SED_CMD 's/^from \([^ ]*\) import \([^ ]*\)_pb2 as \([^ ]*\)$/from snowflake.telemetry._internal.proto_impl.v'"$PB_VERSION_MAJOR"'.\1 import \2_pb2 as \3/' {} +

find proto_impl/v$PB_VERSION_MAJOR -type f \( -name "*.py''" -o -name "*.pyi''" \) -exec rm {} +
