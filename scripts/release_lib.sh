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

# assert_secure_path [path_to_check]
#
# Fail if any directory on the PATH to check (default: $PATH) is unsuitable
# for a release build. A PATH entry is unsuitable when it is empty (meaning
# the current directory), relative, not an existing directory, writable by
# group or others, or owned by anyone other than root or the current user; or
# when any parent directory up to / is writable by group or others without
# the sticky bit (the sticky bit, as on /tmp, prevents non-owners from
# replacing the child) or owned by another user.
#
# The checker's own external commands run from a minimal set of base system
# directories so the result does not depend on the PATH being checked.
#
# For local test builds only, set SNOWFLAKE_TELEMETRY_ALLOW_UNSAFE_PATH=1 to
# bypass this check. Never set it in the Jenkins release job.
assert_secure_path() {
    local path_to_check="${1:-$PATH}"

    if [ "${SNOWFLAKE_TELEMETRY_ALLOW_UNSAFE_PATH:-0}" = "1" ]; then
        echo "WARNING: SNOWFLAKE_TELEMETRY_ALLOW_UNSAFE_PATH=1 is set; skipping the PATH safety check." >&2
        echo "WARNING: never set this for official release builds." >&2
        return 0
    fi

    # Run the checker's own external commands from base system directories
    # only, so the result does not depend on the PATH being checked. PATH
    # keeps its export attribute when reassigned.
    local saved_path="$PATH"
    PATH="/usr/bin:/bin:/usr/sbin:/sbin"

    local current_user
    if ! current_user="$(id -un 2>/dev/null)" || [ -z "$current_user" ]; then
        PATH="$saved_path"
        echo "Unable to determine the current user; refusing to build." >&2
        return 1
    fi

    local failures=""
    local old_ifs="$IFS"
    IFS=':'
    set -f
    # shellcheck disable=SC2086
    set -- $path_to_check
    set +f
    IFS="$old_ifs"

    local entry
    for entry in "$@"; do
        if [ -z "$entry" ]; then
            failures="${failures}  <empty entry> (an empty PATH entry means the current directory)\n"
            continue
        fi
        case "$entry" in
            /*) ;;
            *)
                failures="${failures}  $entry (relative PATH entry)\n"
                continue
                ;;
        esac

        # Canonicalize (resolving symlinks) and confirm it is a directory.
        local dir
        if ! dir="$(cd "$entry" 2>/dev/null && pwd -P)"; then
            failures="${failures}  $entry (does not exist or is not a directory)\n"
            continue
        fi

        # The PATH entry itself must not be writable by group/others at all:
        # anyone who can add files to it can shadow build tools.
        # (-perm /022 = any of the group/other write bits set.)
        if [ -n "$(find "$dir" -prune -perm /022 2>/dev/null)" ]; then
            failures="${failures}  $dir (writable by group or others)\n"
            continue
        fi

        # Walk every component up to /: each must be owned by root or the
        # current user, and must not be writable by group/others unless it is
        # sticky (e.g. /tmp), where the sticky bit stops non-owners from
        # replacing the child.
        local component="$dir"
        while :; do
            if [ -n "$(find "$component" -prune ! -user root ! -user "$current_user" 2>/dev/null)" ]; then
                failures="${failures}  $component (owned by an untrusted user, on PATH via $entry)\n"
                break
            fi
            if [ -n "$(find "$component" -prune -perm /022 ! -perm -1000 2>/dev/null)" ]; then
                failures="${failures}  $component (writable by group or others without sticky bit, on PATH via $entry)\n"
                break
            fi
            [ "$component" = "/" ] && break
            component="$(dirname "$component")"
        done
    done

    PATH="$saved_path"

    if [ -n "$failures" ]; then
        echo "Refusing to build release artifacts with an unsafe PATH." >&2
        echo "Release builds require PATH directories that are not writable by other" >&2
        echo "users. Unsafe entries:" >&2
        printf '%b' "$failures" >&2
        echo "Fix the permissions/ownership above or remove the entries from PATH." >&2
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
