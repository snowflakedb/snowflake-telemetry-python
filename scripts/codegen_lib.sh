#!/bin/bash
#
# Shared helpers for the proto code-generation scripts.
#
# This lives in its own file, and intentionally has NO top-level side effects,
# so the protoc invocation can be exercised directly by unit tests (see
# tests/test_proto_codegen_revision_pin.py) without having to run the full
# clone / virtualenv / pip pipeline that proto_codegen.sh performs.

# checkout_proto_commit <proto_repo_dir> <expected_commit>
#
# Fetch the configured remotes, check out the pinned upstream commit, and
# fail unless HEAD resolves to that exact commit. Only full commit hashes are
# accepted, so the pinned revision cannot change over time.
checkout_proto_commit() {
    local proto_repo_dir="$1"
    local expected_commit="$2"

    if [[ ! "$expected_commit" =~ ^[0-9a-f]{40}$ ]]; then
        echo "OpenTelemetry proto revision must be a full commit hash" >&2
        return 1
    fi

    git -C "$proto_repo_dir" fetch --all
    git -C "$proto_repo_dir" checkout --detach "$expected_commit"

    local actual_commit
    actual_commit="$(git -C "$proto_repo_dir" rev-parse HEAD)"
    if [[ "$actual_commit" != "$expected_commit" ]]; then
        echo "Expected OpenTelemetry proto commit $expected_commit, got $actual_commit" >&2
        return 1
    fi
}

# generate_marshaler_code <proto_repo_dir> <repo_root>
#
# Discover every *.proto file under <proto_repo_dir> and run the custom
# marshaler codegen plugin over them.
#
# The discovered paths are collected NUL-delimited into a bash array and then
# expanded *quoted* ("${all_protos[@]}"), so each filename is passed to protoc
# as exactly one argv element, regardless of whitespace or special characters
# in the name.
generate_marshaler_code() {
    local proto_repo_dir="$1"
    local repo_root="$2"

    # Allow tests to substitute the protoc invocation. This is an internal
    # value, not derived from any discovered filename.
    local protoc_cmd="${PROTOC:-python -m grpc_tools.protoc}"

    local all_protos=()
    local proto_file
    while IFS= read -r -d '' proto_file; do
        all_protos+=("$proto_file")
    done < <(find "$proto_repo_dir/" -iname "*.proto" -print0)

    OPENTELEMETRY_PROTO_DIR="$proto_repo_dir" $protoc_cmd \
        -I "$proto_repo_dir" \
        --plugin=protoc-gen-custom-plugin="$repo_root/scripts/plugin.py" \
        --custom-plugin_out=. \
        "${all_protos[@]}"
}
