import json
import tempfile
import unittest
from pathlib import Path

from captain_core.errors import ManifestError, ManifestNotFoundError, ManifestOwnershipError
from captain_core.manifests import load_tool_manifest, resolve_manifest


def write_manifest(path: Path, tool: str = "stager") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "header": {
            "id": "omni-shell-demo",
            "name": "Omni Shell Demo",
            "tool": tool,
            "category": "filesystems",
            "schemaVersion": "1.0",
            "manifestVersion": "1.0.0"
        },
        "directories": []
    }), encoding="utf-8")


class ManifestTests(unittest.TestCase):
    def test_resolves_short_tool_reference(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            manifest = project / "captain" / "manifests" / "stager" / "filesystems" / "omni-shell-demo.json"
            write_manifest(manifest)
            resolved = resolve_manifest("filesystems/omni-shell-demo", tool="stager", start=project)
            self.assertEqual(resolved, manifest.resolve())

    def test_loads_header_and_validates_ownership(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            manifest = project / "captain" / "manifests" / "stager" / "filesystems" / "omni-shell-demo.json"
            write_manifest(manifest)
            resolved = load_tool_manifest("filesystems/omni-shell-demo", tool="stager", start=project)
            self.assertEqual(resolved.header.id, "omni-shell-demo")

    def test_rejects_wrong_tool_owner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            manifest = project / "captain" / "manifests" / "stager" / "filesystems" / "omni-shell-demo.json"
            write_manifest(manifest, tool="servicewright")
            with self.assertRaises(ManifestOwnershipError):
                load_tool_manifest("filesystems/omni-shell-demo", tool="stager", start=project)

    def test_rejects_reference_traversal(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "captain").mkdir()
            with self.assertRaises(ManifestError):
                resolve_manifest("../other/secret", tool="stager", start=project)

    def test_reports_missing_manifest(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "captain").mkdir()
            with self.assertRaises(ManifestNotFoundError):
                resolve_manifest("filesystems/missing", tool="stager", start=project)


if __name__ == "__main__":
    unittest.main()
