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


if __name__ == "__main__":
    unittest.main()
