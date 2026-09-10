import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RELEASE_LIB = os.path.join(REPO_ROOT, "scripts", "release_lib.sh")
BUILD_SH = os.path.join(REPO_ROOT, "build.sh")
PYPI_BUILD_SH = os.path.join(REPO_ROOT, "pypi-build.sh")
CONDA_BUILD_SH = os.path.join(REPO_ROOT, "anaconda", "build.sh")


def _assert_clean_workspace(repo, extra_env=None):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [
            "bash",
            "-c",
            'source "$1" && assert_clean_workspace "$2"',
            "assert-clean-workspace",
            RELEASE_LIB,
            repo,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def _write_sha256_manifest(dist_dir):
    return subprocess.run(
        [
            "bash",
            "-c",
            'source "$1" && write_sha256_manifest "$2"',
            "write-sha256-manifest",
            RELEASE_LIB,
            dist_dir,
        ],
        capture_output=True,
        text=True,
    )


class TestCleanWorkspaceGate(unittest.TestCase):
    def _git(self, repo, *args, check=True):
        return subprocess.run(
            ["git", "-C", repo, *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def _init_repo(self, repo):
        self._git(repo, "init")
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test User")
        with open(os.path.join(repo, "tracked.txt"), "w") as tracked_file:
            tracked_file.write("tracked\n")
        self._git(repo, "add", "tracked.txt")
        self._git(repo, "commit", "-m", "initial commit")

    def test_pristine_checkout_passes(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            result = _assert_clean_workspace(repo)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_untracked_module_fails(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            # An uncommitted file must fail the gate.
            with open(os.path.join(repo, "setuptools.py"), "w") as shadow:
                shadow.write("# uncommitted file\n")
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("setuptools.py", result.stderr)

    def test_modified_tracked_file_fails(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            with open(os.path.join(repo, "tracked.txt"), "a") as tracked_file:
                tracked_file.write("tampered\n")
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tracked.txt", result.stderr)

    def test_staged_change_fails(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            with open(os.path.join(repo, "staged.txt"), "w") as staged_file:
                staged_file.write("staged\n")
            self._git(repo, "add", "staged.txt")
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("staged.txt", result.stderr)

    def test_ignored_module_in_src_fails(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            # .gitignore ignores local_settings.py at any depth (the real
            # repo's .gitignore does too); ignored files must still fail the
            # gate.
            with open(os.path.join(repo, ".gitignore"), "w") as gitignore:
                gitignore.write("local_settings.py\n")
            self._git(repo, "add", ".gitignore")
            self._git(repo, "commit", "-m", "add gitignore")
            package_dir = os.path.join(repo, "src", "snowflake", "telemetry")
            os.makedirs(package_dir)
            ignored_module = os.path.join(package_dir, "local_settings.py")
            with open(ignored_module, "w") as shadow:
                shadow.write("# uncommitted file\n")
            check_ignore = self._git(
                repo, "check-ignore", "src/snowflake/telemetry/local_settings.py"
            )
            self.assertEqual(check_ignore.returncode, 0)
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local_settings.py", result.stderr)

    def test_ignored_stale_build_dir_fails(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            # Ignored directories (e.g. build/) must fail the gate like any
            # other leftover.
            with open(os.path.join(repo, ".gitignore"), "w") as gitignore:
                gitignore.write("build/\n")
            self._git(repo, "add", ".gitignore")
            self._git(repo, "commit", "-m", "add gitignore")
            stale_dir = os.path.join(repo, "build", "lib", "snowflake", "telemetry")
            os.makedirs(stale_dir)
            with open(os.path.join(stale_dir, "stray.py"), "w") as planted:
                planted.write("# leftover file\n")
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("build/", result.stderr)

    def test_opt_out_env_var_bypasses_with_warning(self):
        with tempfile.TemporaryDirectory() as repo:
            self._init_repo(repo)
            with open(os.path.join(repo, "setuptools.py"), "w") as shadow:
                shadow.write("# local test only\n")
            result = _assert_clean_workspace(
                repo,
                extra_env={"SNOWFLAKE_TELEMETRY_ALLOW_DIRTY_WORKSPACE": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("WARNING", result.stderr)

    def test_non_git_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as repo:
            result = _assert_clean_workspace(repo)
            self.assertNotEqual(result.returncode, 0)


class TestReleaseScriptsEnforceHygiene(unittest.TestCase):
    def test_build_sh_gates_on_clean_workspace(self):
        with open(BUILD_SH) as build_script:
            script = build_script.read()
        self.assertIn("release_lib.sh", script)
        # The explicit exit keeps the gate effective even when the script is
        # invoked as `bash build.sh` without the shebang's -e flag.
        self.assertIn('assert_clean_workspace "${REPO_ROOT}" || exit 1', script)

    def test_build_sh_records_full_head_commit(self):
        with open(BUILD_SH) as build_script:
            script = build_script.read()
        self.assertIn("rev-parse HEAD", script)
        self.assertNotIn("rev-parse --short HEAD", script)

    def test_build_sh_writes_sha256_manifest(self):
        with open(BUILD_SH) as build_script:
            script = build_script.read()
        self.assertIn("write_sha256_manifest ./anaconda/dist || exit 1", script)

    def test_pypi_build_sh_gates_on_clean_workspace(self):
        with open(PYPI_BUILD_SH) as build_script:
            script = build_script.read()
        self.assertIn("release_lib.sh", script)
        self.assertIn('assert_clean_workspace "${REPO_ROOT}" || exit 1', script)
        self.assertIn("write_sha256_manifest ./dist || exit 1", script)

    def test_conda_build_runs_python_isolated(self):
        with open(CONDA_BUILD_SH) as build_script:
            script = build_script.read()
        self.assertIn("${PYTHON} -I setup.py", script)


class TestSha256Manifest(unittest.TestCase):
    def test_manifest_records_artifact_digests(self):
        with tempfile.TemporaryDirectory() as dist:
            payload = b"artifact-bytes"
            with open(os.path.join(dist, "pkg-1.0.tar.bz2"), "wb") as artifact:
                artifact.write(payload)
            result = _write_sha256_manifest(dist)
            self.assertEqual(result.returncode, 0, result.stderr)

            manifest_path = os.path.join(dist, "SHA256SUMS")
            with open(manifest_path) as manifest:
                entries = manifest.read()
            expected_digest = hashlib.sha256(payload).hexdigest()
            self.assertIn(expected_digest, entries)
            self.assertIn("pkg-1.0.tar.bz2", entries)

    def test_manifest_fails_closed_without_artifacts(self):
        with tempfile.TemporaryDirectory() as dist:
            result = _write_sha256_manifest(dist)
            self.assertNotEqual(result.returncode, 0)


class TestBuildScriptsEndToEnd(unittest.TestCase):
    """Run the real release scripts in a temp repo.

    The scripts are invoked as `bash <script>` (no -e from the shebang) to
    prove the hygiene gate aborts the build regardless of how Jenkins calls
    them.
    """

    def _git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", repo, *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _make_repo(self, repo, script_name):
        os.mkdir(os.path.join(repo, "scripts"))
        shutil.copy(os.path.join(REPO_ROOT, script_name), os.path.join(repo, script_name))
        shutil.copy(RELEASE_LIB, os.path.join(repo, "scripts", "release_lib.sh"))
        self._git(repo, "init")
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test User")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-m", "initial commit")

    def test_build_sh_fails_at_gate_when_workspace_dirty(self):
        with tempfile.TemporaryDirectory() as repo:
            self._make_repo(repo, "build.sh")
            with open(os.path.join(repo, "setuptools.py"), "w") as shadow:
                shadow.write("# uncommitted file\n")
            result = subprocess.run(
                ["bash", "build.sh"],
                cwd=repo,
                capture_output=True,
                text=True,
            )
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-pristine", output)
            # The build must never start: conda is not installed in the test
            # environment, so reaching it would surface a command error.
            self.assertNotIn("Start building", output)
            self.assertNotIn("command not found", output)

    def test_build_sh_proceeds_past_gate_when_pristine(self):
        with tempfile.TemporaryDirectory() as base:
            repo = os.path.join(base, "repo")
            os.mkdir(repo)
            self._make_repo(repo, "build.sh")
            # Stub out conda so the script can run past the gate without a
            # real conda installation. The stub must live outside the repo or
            # it would itself trip the hygiene gate.
            stub_bin = os.path.join(base, "stub-bin")
            os.mkdir(stub_bin)
            stub = os.path.join(stub_bin, "conda")
            with open(stub, "w") as stub_file:
                stub_file.write("#!/bin/bash\nexit 0\n")
            os.chmod(stub, stat.S_IRWXU)
            env = dict(os.environ)
            env["PATH"] = stub_bin + os.pathsep + env["PATH"]
            result = subprocess.run(
                ["bash", "build.sh"],
                cwd=repo,
                capture_output=True,
                text=True,
                env=env,
            )
            output = result.stdout + result.stderr
            # The gate passes and the build starts; the run then fails closed
            # because the stubbed conda build produced no artifacts to digest.
            self.assertIn("Start building", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No build artifacts", output)

    def test_pypi_build_sh_fails_at_gate_when_workspace_dirty(self):
        with tempfile.TemporaryDirectory() as repo:
            self._make_repo(repo, "pypi-build.sh")
            with open(os.path.join(repo, "setuptools.py"), "w") as shadow:
                shadow.write("# uncommitted file\n")
            result = subprocess.run(
                ["bash", "pypi-build.sh"],
                cwd=repo,
                capture_output=True,
                text=True,
            )
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-pristine", output)
            # The build must never start: no build venv may be created.
            self.assertEqual(
                [name for name in os.listdir(repo) if name.startswith("venv_")],
                [],
            )


class TestIsolatedPythonImport(unittest.TestCase):
    def test_isolated_mode_imports_trusted_module(self):
        with tempfile.TemporaryDirectory() as base:
            venv_dir = os.path.join(base, "venv")
            try:
                subprocess.run(
                    [sys.executable, "-m", "venv", "--without-pip", venv_dir],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as error:
                self.skipTest("venv unavailable: %s" % error.stderr)
            venv_python = os.path.join(venv_dir, "bin", "python")

            # Install a stand-in for the trusted setuptools module into the
            # environment's site-packages.
            purelib = subprocess.run(
                [venv_python, "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            os.makedirs(purelib, exist_ok=True)
            with open(os.path.join(purelib, "setuptools.py"), "w") as trusted:
                trusted.write(
                    "def setup(**kwargs):\n"
                    "    print('TRUSTED:' + kwargs.get('name', ''))\n"
                )

            # A minimal build script plus a same-directory stand-in module.
            work = os.path.join(base, "work")
            os.mkdir(work)
            with open(os.path.join(work, "setup.py"), "w") as setup_py:
                setup_py.write(
                    "from setuptools import setup\n"
                    "setup(name='isolated-demo')\n"
                )
            marker = os.path.join(base, "marker")
            with open(os.path.join(work, "setuptools.py"), "w") as shadow:
                shadow.write(
                    "open(%r, 'w').write('local')\n"
                    "def setup(**kwargs):\n"
                    "    print('LOCAL')\n" % marker
                )

            # Default behavior: the script's directory is on sys.path, so the
            # same-directory module is imported.
            result = subprocess.run(
                [venv_python, "setup.py"],
                cwd=work,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("LOCAL", result.stdout)
            self.assertTrue(os.path.exists(marker))
            os.remove(marker)

            # Isolated mode (-I), as used by anaconda/build.sh: the script's
            # directory is removed from sys.path and the trusted module wins.
            result = subprocess.run(
                [venv_python, "-I", "setup.py"],
                cwd=work,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("TRUSTED:isolated-demo", result.stdout)
            self.assertFalse(os.path.exists(marker))


if __name__ == "__main__":
    unittest.main()
