import os
import subprocess
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CODEGEN_LIB = os.path.join(REPO_ROOT, "scripts", "codegen_lib.sh")
CODEGEN_SCRIPT = os.path.join(REPO_ROOT, "scripts", "proto_codegen.sh")
EXPECTED_V1_7_0_COMMIT = "8654ab7a5a43ca25fe8046e59dcd6935c3f76de0"


class TestProtoCodegenRevisionPin(unittest.TestCase):
    def _git(self, repo, *args, check=True):
        return subprocess.run(
            ["git", "-C", repo, *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def _checkout_proto_commit(self, repo, commit):
        return subprocess.run(
            [
                "bash",
                "-c",
                'source "$1" && checkout_proto_commit "$2" "$3"',
                "checkout-proto-commit",
                CODEGEN_LIB,
                repo,
                commit,
            ],
            capture_output=True,
            text=True,
        )

    def test_codegen_script_pins_v1_7_0_to_immutable_commit(self):
        with open(CODEGEN_SCRIPT) as script_file:
            script = script_file.read()

        self.assertIn(
            'PROTO_REPO_COMMIT="%s"' % EXPECTED_V1_7_0_COMMIT,
            script,
        )
        self.assertIn(
            'checkout_proto_commit "$PROTO_REPO_DIR" "$PROTO_REPO_COMMIT"',
            script,
        )

    def test_checkout_uses_pinned_commit_after_tag_moves(self):
        with tempfile.TemporaryDirectory() as repo:
            self._git(repo, "init")
            self._git(repo, "config", "user.email", "test@example.com")
            self._git(repo, "config", "user.name", "Test User")

            tracked_file = os.path.join(repo, "revision.txt")
            with open(tracked_file, "w") as revision_file:
                revision_file.write("trusted\n")
            self._git(repo, "add", "revision.txt")
            self._git(repo, "commit", "-m", "trusted revision")
            trusted_commit = self._git(repo, "rev-parse", "HEAD").stdout.strip()
            self._git(repo, "tag", "v1.7.0")

            with open(tracked_file, "w") as revision_file:
                revision_file.write("moved tag\n")
            self._git(repo, "commit", "-am", "move tag target")
            moved_commit = self._git(repo, "rev-parse", "HEAD").stdout.strip()
            self._git(repo, "tag", "-f", "v1.7.0")
            self.assertNotEqual(trusted_commit, moved_commit)

            result = self._checkout_proto_commit(repo, trusted_commit)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                self._git(repo, "rev-parse", "HEAD").stdout.strip(),
                trusted_commit,
            )
            self.assertNotEqual(
                self._git(repo, "rev-parse", "v1.7.0").stdout.strip(),
                trusted_commit,
            )
            self.assertNotEqual(
                self._git(repo, "symbolic-ref", "-q", "HEAD", check=False).returncode,
                0,
            )

    def test_checkout_fails_closed_for_unknown_commit(self):
        with tempfile.TemporaryDirectory() as repo:
            self._git(repo, "init")
            result = self._checkout_proto_commit(repo, "0" * 40)
            self.assertNotEqual(result.returncode, 0)

    def test_checkout_rejects_movable_tag(self):
        with tempfile.TemporaryDirectory() as repo:
            self._git(repo, "init")
            result = self._checkout_proto_commit(repo, "v1.7.0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("full commit hash", result.stderr)


class TestGenerateMarshalerCode(unittest.TestCase):
    def _generate_argv(self, proto_dir, repo_root):
        # Run generate_marshaler_code with a stubbed protoc and return the
        # argv it received (one element per line).
        with tempfile.TemporaryDirectory() as work:
            argv_file = os.path.join(work, "argv")
            stub = os.path.join(work, "protoc-stub")
            with open(stub, "w") as stub_file:
                stub_file.write('#!/bin/bash\nprintf \'%s\\n\' "$@" > "$ARGV_CAPTURE"\n')
            os.chmod(stub, 0o755)
            env = dict(os.environ)
            env["PROTOC"] = stub
            env["ARGV_CAPTURE"] = argv_file
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1" && generate_marshaler_code "$2" "$3"',
                    "generate-marshaler-code",
                    CODEGEN_LIB,
                    proto_dir,
                    repo_root,
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with open(argv_file) as captured:
                return captured.read().splitlines()

    def test_filenames_with_spaces_pass_as_single_argument(self):
        with tempfile.TemporaryDirectory() as proto_dir, tempfile.TemporaryDirectory() as repo_root:
            spaced_dir = os.path.join(proto_dir, "dir with spaces")
            os.makedirs(spaced_dir)
            proto_file = os.path.join(spaced_dir, "file.proto")
            open(proto_file, "w").close()

            argv = self._generate_argv(proto_dir, repo_root)

            self.assertEqual(argv[0], "-I")
            self.assertEqual(argv[1], proto_dir)
            self.assertEqual(
                argv[2],
                "--plugin=protoc-gen-custom-plugin=%s"
                % os.path.join(repo_root, "scripts", "plugin.py"),
            )
            self.assertEqual(argv[3], "--custom-plugin_out=.")
            self.assertEqual(argv[4:], [proto_file])

    def test_no_extra_protoc_options_from_filenames(self):
        with tempfile.TemporaryDirectory() as proto_dir, tempfile.TemporaryDirectory() as repo_root:
            option_like_dir = os.path.join(
                proto_dir, "x --plugin=protoc-gen-custom-plugin=other"
            )
            os.makedirs(option_like_dir)
            proto_file = os.path.join(option_like_dir, "y.proto")
            open(proto_file, "w").close()

            argv = self._generate_argv(proto_dir, repo_root)

            plugin_options = [arg for arg in argv if arg.startswith("--plugin=")]
            self.assertEqual(
                plugin_options,
                [
                    "--plugin=protoc-gen-custom-plugin=%s"
                    % os.path.join(repo_root, "scripts", "plugin.py")
                ],
            )
            self.assertIn(proto_file, argv)


if __name__ == "__main__":
    unittest.main()
