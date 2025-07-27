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
PROTO_REPO_BRANCH_OR_COMMIT="v1.7.0"

set -e

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
mkdir -p opentelemetry/proto
find opentelemetry/proto/ -regex ".*_marshaler\.py" -exec rm {} +

# generate proto code for all protos
all_protos=$(find $PROTO_REPO_DIR/ -iname "*.proto")
OPENTELEMETRY_PROTO_DIR=$PROTO_REPO_DIR python -m grpc_tools.protoc \
    -I $PROTO_REPO_DIR \
    --plugin=protoc-gen-custom-plugin=$repo_root/scripts/plugin.py \
    --custom-plugin_out=. \
    $all_protos
