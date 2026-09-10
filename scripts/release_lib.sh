# Guards for the Jenkins release build scripts (build.sh and pypi-build.sh).
#
# This file is sourced by those scripts and by the unit tests in
# tests/test_release_build_hygiene.py. It must only define functions and have
# no side effects when sourced.

# assert_clean_workspace <repo_root>
#
# Return 0 only when the git working tree at <repo_root> is pristine: no
# modified, staged, untracked, or ignored files. Otherwise print the offending
# entries to stderr and return 1.
#
# Release builds must produce artifacts from committed sources only, so the
# build refuses to run from a checkout with any leftover or unreviewed files.
#
# For local test builds only, set SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE=1
# to bypass this check. Never set it in the Jenkins release job.
assert_clean_workspace() {
    local repo_root="${1:-}"

    if [ -z "$repo_root" ]; then
        echo "assert_clean_workspace: no repository path given; refusing to build." >&2
        return 1
    fi

    if [ "${SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE:-0}" = "1" ]; then
        echo "WARNING: SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE=1 is set; skipping the workspace hygiene check." >&2
        echo "WARNING: never set this for official release builds." >&2
        return 0
    fi

    local status
    if ! status="$(git -C "$repo_root" status --porcelain --untracked-files=all --ignored=matching 2>&1)"; then
        echo "Unable to determine the git state of $repo_root; refusing to build." >&2
        echo "$status" >&2
        return 1
    fi

    if [ -n "$status" ]; then
        echo "Refusing to build release artifacts from a non-pristine workspace: $repo_root" >&2
        echo "The following modified, untracked, or ignored (!!) files are present:" >&2
        echo "$status" >&2
        echo "Release builds must run from a pristine checkout so that artifacts" >&2
        echo "contain only committed sources." >&2
        return 1
    fi
}

# write_sha256_manifest <dist_dir>
#
# Write <dist_dir>/SHA256SUMS containing the SHA-256 digest of every file
# under <dist_dir>, so downstream release steps can verify that the artifacts
# they publish are bit-for-bit what this build produced. Fails if no artifacts
# are present.
write_sha256_manifest() {
    local dist_dir="${1:-}"

    if [ -z "$dist_dir" ] || [ ! -d "$dist_dir" ]; then
        echo "write_sha256_manifest: '$dist_dir' is not a directory." >&2
        return 1
    fi

    local sha256_cmd
    if command -v sha256sum >/dev/null 2>&1; then
        sha256_cmd="sha256sum"
    else
        # macOS (local test builds) ships shasum instead of sha256sum.
        sha256_cmd="shasum -a 256"
    fi

    local files
    files="$(cd "$dist_dir" && find . -type f ! -name SHA256SUMS -print | sort)"
    if [ -z "$files" ]; then
        echo "No build artifacts found under $dist_dir" >&2
        return 1
    fi

    (cd "$dist_dir" && printf '%s\n' "$files" | while IFS= read -r artifact; do
        $sha256_cmd "$artifact"
    done > SHA256SUMS)
}
