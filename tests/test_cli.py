import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CaptainCoreCliTests(unittest.TestCase):
    def _project(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "manifest.json").write_text(json.dumps({
            "schema": "captain/manifest/v1",
            "project": {"name": "sample", "type": "native", "version": "1.0.0"},
            "embark": {"package": {"name": "sample"}},
        }))
        return root

    def test_resolves_tool_config_as_json(self):
        root = self._project()
        result = subprocess.run([
            sys.executable, "-m", "captain_core", "manifest", "resolve",
            "--project", str(root), "--tool", "embark", "--required", "--json",
        ], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["tool"], "embark")
        self.assertTrue(payload["inline"])
        self.assertEqual(payload["config"]["package"]["name"], "sample")

    def test_required_missing_tool_returns_error(self):
        root = self._project()
        result = subprocess.run([
            sys.executable, "-m", "captain_core", "manifest", "resolve",
            "--project", str(root), "--tool", "stager", "--required", "--json",
        ], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('configuration "stager" is required', result.stderr)


if __name__ == "__main__":
    unittest.main()
