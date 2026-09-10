#!/bin/bash
#
# Regenerate python code from OTLP protos in
# https://github.com/open-telemetry/opentelemetry-proto
#
# To use, update PROTO_REPO_COMMIT below to the full commit hash in the
# opentelemetry-proto repository that you want to build from. Then, just run
# this script to update the proto files. Commit the changes as well as any
# fixes needed in the OTLP exporter.
#
# Optional envars:
#   PROTO_REPO_DIR - the path to an existing checkout of the opentelemetry-proto repo

# Immutable commit for opentelemetry-proto v1.7.0.
PROTO_REPO_COMMIT="8654ab7a5a43ca25fe8046e59dcd6935c3f76de0"

set -e

PROTO_REPO_DIR=${PROTO_REPO_DIR:-"/tmp/opentelemetry-proto"}
# root of opentelemetry-python repo
repo_root="$(git rev-parse --show-toplevel)"
venv_dir="/tmp/proto_codegen_venv"

# Shared codegen helpers (defines generate_marshaler_code). Sourcing has no
# side effects; it only defines functions.
source "$repo_root/scripts/codegen_lib.sh"

# run on exit even if crash
cleanup() {
    echo "Deleting $venv_dir"
    rm -rf $venv_dir
}
trap cleanup EXIT

echo "Creating temporary virtualenv at $venv_dir using $(python3 --version)"
python3 -m venv $venv_dir
source $venv_dir/bin/activate
python -m pip install \
    -c $repo_root/scripts/gen-requirements.txt \
    protobuf Jinja2 grpcio-tools black isort .

echo 'python -m grpc_tools.protoc --version'
python -m grpc_tools.protoc --version

# Clone the proto repo if it doesn't exist
if [ ! -d "$PROTO_REPO_DIR" ]; then
    git clone https://github.com/open-telemetry/opentelemetry-proto.git $PROTO_REPO_DIR
fi

# Fetch and check out the pinned upstream revision.
checkout_proto_commit "$PROTO_REPO_DIR" "$PROTO_REPO_COMMIT"

cd $repo_root/src/snowflake/telemetry/_internal

# clean up old generated code
mkdir -p opentelemetry/proto
find opentelemetry/proto/ -regex ".*_marshaler\.py" -exec rm {} +

# generate proto code for all protos
# Proto paths are discovered and passed to protoc by generate_marshaler_code,
# which collects them into a quoted bash array so each filename is passed as a
# single argument. See scripts/codegen_lib.sh.
generate_marshaler_code "$PROTO_REPO_DIR" "$repo_root"
