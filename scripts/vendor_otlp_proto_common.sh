#!/bin/bash
#
# Vendor in the python code in
# https://github.com/open-telemetry/opentelemetry-python/tree/main/exporter/opentelemetry-exporter-otlp-proto-common/src/opentelemetry/exporter/otlp/proto/common
#
# To use, update REPO_BRANCH_OR_COMMIT variable below to a commit hash or
# tag in opentelemtry-python repo that you want to build off of. Then, just run
# this script to update the proto files. Commit the changes as well as any
# fixes needed in the OTLP exporter.

# Pinned commit/branch/tag for the current version used in opentelemetry-proto python package.
REPO_BRANCH_OR_COMMIT="v1.35.0"

set -e

REPO_DIR=${REPO_DIR:-"/tmp/opentelemetry-python"}
# root of opentelemetry-python repo
repo_root="$(git rev-parse --show-toplevel)"

# Clone the proto repo if it doesn't exist
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/open-telemetry/opentelemetry-python.git $REPO_DIR
fi

# Pull in changes and switch to requested branch
(
    cd $REPO_DIR
    git fetch --all
    git checkout $REPO_BRANCH_OR_COMMIT
    # pull if REPO_BRANCH_OR_COMMIT is not a detached head
    git symbolic-ref -q HEAD && git pull --ff-only || true
)

cd $repo_root/src/snowflake/telemetry/_internal

# Copy the entire file tree from exporter/opentelemetry-exporter-otlp-proto-common/src/opentelemetry/
# to src/snowflake/telemetry/_internal/opentelemetry/
cp -r $REPO_DIR/exporter/opentelemetry-exporter-otlp-proto-common/src/opentelemetry/exporter opentelemetry/

# If MacOS need '' after -i
# Detect the OS (macOS or Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD="sed -i ''"
else
  SED_CMD="sed -i"
fi

# Replace all the imports strings in the copied python files
#   opentelemetry.exporter to snowflake.telemetry._internal.opentelemetry.exporter
#   opentelemetry.proto.*_pb2 to snowflake.telemetry._internal.opentelemetry.proto.*_marshaler

find opentelemetry/exporter -type f -name "*.py" -exec $SED_CMD 's/opentelemetry.exporter/snowflake.telemetry._internal.opentelemetry.exporter/g' {} +
find opentelemetry/exporter -type f -name "*.py" -exec $SED_CMD 's/opentelemetry\.proto\(.*\)_pb2/snowflake.telemetry._internal.opentelemetry.proto\1_marshaler/g' {} +


# Add a notice to the top of every file in compliance with Apache 2.0 to indicate that the file has been modified
# https://www.apache.org/licenses/LICENSE-2.0
find opentelemetry/exporter -type f -name "*.py" -exec $SED_CMD '14s|^|#\n# This file has been modified from the original source code at\n#\n#     https://github.com/open-telemetry/opentelemetry-python/tree/'"$REPO_BRANCH_OR_COMMIT"'\n#\n# by Snowflake Inc.\n|' {} +
