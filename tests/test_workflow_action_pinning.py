import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".github", "workflows")

# Captures the ref of a `uses:` step, stopping at whitespace or a comment.
USES_PATTERN = re.compile(r"uses:\s*([^\s#]+)")

# A `uses:` ref is only immutable when pinned to a full-length commit SHA.
PINNED_SHA_PATTERN = re.compile(r"^[^\s/]+/[^\s/]+@[0-9a-f]{40}$")


class TestWorkflowActionPinning(unittest.TestCase):
    def _workflow_files(self):
        workflow_files = [
            os.path.join(WORKFLOWS_DIR, name)
            for name in sorted(os.listdir(WORKFLOWS_DIR))
            if name.endswith((".yml", ".yaml"))
        ]
        self.assertTrue(workflow_files, "no workflow files found")
        return workflow_files

    def test_all_action_refs_are_pinned_to_commit_shas(self):
        # Mutable action refs (e.g. actions/setup-python@v3 or
        # pypa/gh-action-pypi-publish@release/v1) can change what runs in CI
        # and release workflows over time. Every action ref must therefore be
        # pinned to a full commit SHA so runs are reproducible.
        unpinned = []
        for workflow in self._workflow_files():
            with open(workflow) as workflow_file:
                for line_number, line in enumerate(workflow_file, start=1):
                    if line.lstrip().startswith("#"):
                        continue
                    match = USES_PATTERN.search(line)
                    if not match:
                        continue
                    ref = match.group(1)
                    if not PINNED_SHA_PATTERN.match(ref):
                        unpinned.append(
                            "%s:%d: %s"
                            % (os.path.basename(workflow), line_number, ref)
                        )
        self.assertEqual(
            unpinned,
            [],
            "action refs not pinned to full commit SHAs: %s" % unpinned,
        )

    def test_release_workflow_records_artifact_digests(self):
        # The release workflow must record SHA-256 digests of
        # the built artifacts so the published files can be compared against
        # what the release job actually produced.
        with open(os.path.join(WORKFLOWS_DIR, "python-publish.yml")) as workflow_file:
            workflow = workflow_file.read()
        self.assertIn("sha256sum dist/*", workflow)

    def test_release_publish_action_is_pinned(self):
        # The publish step is the most sensitive action ref in the
        # repository.
        with open(os.path.join(WORKFLOWS_DIR, "python-publish.yml")) as workflow_file:
            workflow = workflow_file.read()
        match = re.search(r"uses:\s*(pypa/gh-action-pypi-publish@[^\s#]+)", workflow)
        self.assertIsNotNone(match, "publish step not found")
        self.assertRegex(match.group(1), r"@[0-9a-f]{40}$")

    def test_release_workflow_installs_only_pinned_pip_packages(self):
        # Installing unpinned ("latest") packages at release time makes the
        # release non-reproducible. Every pip install must pin an exact
        # version with ==.
        with open(os.path.join(WORKFLOWS_DIR, "python-publish.yml")) as workflow_file:
            workflow = workflow_file.read()
        install_lines = [
            line.strip()
            for line in workflow.splitlines()
            if "pip install" in line
        ]
        self.assertTrue(install_lines, "no pip install lines found in release workflow")
        for line in install_lines:
            self.assertIn("==", line, "unpinned pip install in release workflow: %s" % line)


if __name__ == "__main__":
    unittest.main()
