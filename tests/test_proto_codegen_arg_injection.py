"""
Security regression test for CWE-88 argument injection in the proto codegen
scripts.

``scripts/proto_codegen.sh`` regenerates the marshaler code by discovering every
``*.proto`` file under an upstream checkout and passing the paths to ``protoc``.
A prior version expanded the discovered paths as an *unquoted* shell scalar
(``$all_protos``), so an attacker who could introduce a specially named
``.proto`` file into the upstream repo -- reachable because the source is pinned
only to a movable tag (``v1.7.0``) -- could smuggle extra ``protoc`` options into
the command line via shell word-splitting. In particular a second
``--plugin=protoc-gen-custom-plugin=<attacker path>`` would override the trusted
plugin, causing ``protoc`` to execute an attacker-controlled binary on the
codegen / CI host.

The fix lives in ``scripts/codegen_lib.sh`` (``generate_marshaler_code``), which
collects the discovered paths NUL-delimited into a bash array and expands them
quoted, so every filename is a single argv element that can never be
re-interpreted as a ``protoc`` option.

This test drives the real ``generate_marshaler_code`` function with a maliciously
named ``.proto`` file and a fake ``protoc`` that records the exact argv it
receives. It asserts that:

  * the malicious filename arrives as a single argument, and
  * the only custom plugin ``protoc`` is told to use is the trusted
    ``scripts/plugin.py`` -- never the attacker's path.

On the vulnerable (unquoted) implementation both assertions fail.
"""
import json
import os
import subprocess
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CODEGEN_LIB = os.path.join(REPO_ROOT, "scripts", "codegen_lib.sh")
TRUSTED_PLUGIN = os.path.join(REPO_ROOT, "scripts", "plugin.py")
PLUGIN_PREFIX = "--plugin=protoc-gen-custom-plugin="


class TestProtoCodegenArgInjection(unittest.TestCase):
    def _run_generate(self, proto_repo_dir, args_file, fake_protoc):
        env = dict(os.environ)
        # Substitute protoc with our recorder; path has no spaces so the
        # internal word-split of PROTOC is safe.
        env["PROTOC"] = "python3 " + fake_protoc
        env["PROTOC_ARGS_FILE"] = args_file
        script = (
            'source "%s" && generate_marshaler_code "%s" "%s"'
            % (CODEGEN_LIB, proto_repo_dir, REPO_ROOT)
        )
        # Run from a scratch cwd so the `--custom-plugin_out=.` is harmless.
        result = subprocess.run(
            ["bash", "-c", script],
            cwd=tempfile.gettempdir(),
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            "generate_marshaler_code exited non-zero.\n"
            "stdout:\n%s\nstderr:\n%s" % (result.stdout, result.stderr),
        )

    def test_malicious_proto_filename_cannot_inject_protoc_options(self):
        self.assertTrue(
            os.path.exists(CODEGEN_LIB),
            "scripts/codegen_lib.sh is missing; the codegen helper must expose "
            "generate_marshaler_code for the argument-injection fix.",
        )

        with tempfile.TemporaryDirectory() as tmp:
            proto_repo_dir = os.path.join(tmp, "opentelemetry-proto")
            os.makedirs(proto_repo_dir)

            # Fake protoc that records the exact argv it receives as JSON.
            fake_protoc = os.path.join(tmp, "fake_protoc.py")
            args_file = os.path.join(tmp, "protoc_argv.json")
            with open(fake_protoc, "w") as f:
                f.write(
                    "import json, os, sys\n"
                    "with open(os.environ['PROTOC_ARGS_FILE'], 'w') as fh:\n"
                    "    json.dump(sys.argv[1:], fh)\n"
                )

            # The attacker's plugin token they attempt to smuggle in. A real
            # filename component cannot contain "/", so the injected token is
            # slash-free here; in a real attack the attacker nests directories
            # so that find's output reconstructs an executable path. That
            # nesting is irrelevant to the word-splitting mechanism this test
            # exercises.
            evil_token = "evil_plugin_exec"
            evil_opt = PLUGIN_PREFIX + evil_token

            # A single .proto file whose name, if word-split, becomes:
            #   good1.proto  --plugin=protoc-gen-custom-plugin=<evil>  good2.proto
            malicious_name = "good1.proto " + evil_opt + " good2.proto"
            malicious_path = os.path.join(proto_repo_dir, malicious_name)
            with open(malicious_path, "w") as f:
                f.write('syntax = "proto3";\n')

            self._run_generate(proto_repo_dir, args_file, fake_protoc)

            with open(args_file) as f:
                argv = json.load(f)

            # 1) The malicious filename must arrive as ONE argv element (i.e.
            #    some argv element ends with the full crafted basename). If it
            #    was word-split, no single element contains the whole name.
            self.assertTrue(
                any(a.endswith(malicious_name) for a in argv),
                "Malicious proto path was word-split rather than passed as a "
                "single argument -- this is the argument-injection bug.\n"
                "argv = %r" % (argv,),
            )

            # 2) protoc must be told about exactly one custom plugin, and it
            #    must be the trusted scripts/plugin.py -- never the attacker's.
            plugin_opts = [a for a in argv if a.startswith(PLUGIN_PREFIX)]
            self.assertEqual(
                [PLUGIN_PREFIX + TRUSTED_PLUGIN],
                plugin_opts,
                "An attacker-controlled --plugin option was injected via the "
                "proto filename.\nargv = %r" % (argv,),
            )

            # 3) The attacker's plugin option must not appear as a standalone
            #    argument at all.
            self.assertNotIn(
                evil_opt,
                argv,
                "Attacker plugin option leaked into protoc argv as a standalone "
                "token.\nargv = %r" % (argv,),
            )


if __name__ == "__main__":
    unittest.main()
