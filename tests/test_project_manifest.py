import json
import tempfile
import unittest
from pathlib import Path

from captain_core.errors import ManifestError, ManifestNotFoundError, ManifestOwnershipError
from captain_core.project_manifest import (
    CAPTAIN_MANIFEST_SCHEMA,
    CAPTAIN_TOOL_MANIFEST_SCHEMA,
    get_captain_manifest_path,
    get_manifest_section,
    load_captain_manifest,
    resolve_tool_config,
)


class ProjectManifestTests(unittest.TestCase):
    def write_manifest(self, project: Path, **sections):
        document = {
            "schema": CAPTAIN_MANIFEST_SCHEMA,
            "project": {
                "name": "sample",
                "type": "native",
                "version": "1.0.0",
            },
            "versionLanes": {},
            "components": [],
            **sections,
        }
        (project / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
        return document

    def write_tool_manifest(self, project: Path, tool: str, config: dict, *, owner=None):
        manifests = project / "manifests"
        manifests.mkdir(parents=True, exist_ok=True)
        path = manifests / f"{tool}.json"
        path.write_text(
            json.dumps({
                "schema": CAPTAIN_TOOL_MANIFEST_SCHEMA,
                "tool": owner or tool,
                "config": config,
            }),
            encoding="utf-8",
        )
        return path

    def test_canonical_manifest_is_owned_by_project_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.assertEqual(
                get_captain_manifest_path(start=project),
                (project / "manifest.json").resolve(),
            )

    def test_loads_unified_manifest(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_manifest(project, dockhand={"ports": []})
            resolved = load_captain_manifest(start=project)
            self.assertEqual(resolved.document["project"]["name"], "sample")
            self.assertEqual(get_manifest_section(resolved.document, "dockhand"), {"ports": []})

    def test_resolves_inline_tool_configuration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_manifest(project, stager={"target": "linux"})
            resolved = resolve_tool_config("stager", start=project, required=True)
            self.assertTrue(resolved.inline)
            self.assertEqual(resolved.path, (project / "manifest.json").resolve())
            self.assertEqual(resolved.config, {"target": "linux"})

    def test_resolves_split_tool_configuration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_tool_manifest(project, "stager", {"target": "linux"})
            self.write_manifest(project, manifests={"stager": "manifests/stager.json"})
            resolved = resolve_tool_config("stager", start=project, required=True)
            self.assertFalse(resolved.inline)
            self.assertEqual(resolved.path, (project / "manifests" / "stager.json").resolve())
            self.assertEqual(resolved.config, {"target": "linux"})

    def test_supports_hybrid_manifest_layout(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_tool_manifest(project, "embark", {"formats": ["deb"]})
            self.write_manifest(
                project,
                build={"schema": "captain/build/v0.1"},
                manifests={"embark": "manifests/embark.json"},
            )
            build = resolve_tool_config("build", start=project, required=True)
            embark = resolve_tool_config("embark", start=project, required=True)
            self.assertTrue(build.inline)
            self.assertFalse(embark.inline)

    def test_rejects_duplicate_inline_and_referenced_tool_configuration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_tool_manifest(project, "stager", {"target": "linux"})
            self.write_manifest(
                project,
                stager={"target": "linux"},
                manifests={"stager": "manifests/stager.json"},
            )
            with self.assertRaises(ManifestError):
                resolve_tool_config("stager", start=project)

    def test_rejects_wrong_split_manifest_owner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_tool_manifest(project, "stager", {}, owner="embark")
            self.write_manifest(project, manifests={"stager": "manifests/stager.json"})
            with self.assertRaises(ManifestOwnershipError):
                resolve_tool_config("stager", start=project)

    def test_rejects_split_manifest_reference_traversal(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            with self.assertRaises(ManifestError):
                self.write_manifest(project, manifests={"stager": "../stager.json"})
                load_captain_manifest(start=project)

    def test_missing_optional_section_returns_none(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            document = self.write_manifest(project)
            self.assertIsNone(get_manifest_section(document, "embark"))
            self.assertIsNone(resolve_tool_config("embark", start=project))

    def test_required_tool_configuration_must_exist(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_manifest(project)
            with self.assertRaises(ManifestError):
                resolve_tool_config("servicewright", start=project, required=True)

    def test_rejects_non_object_inline_tool_section(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            document = self.write_manifest(project, embark=[])
            with self.assertRaises(ManifestError):
                get_manifest_section(document, "embark")

    def test_reports_missing_captain_manifest_in_selected_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            with self.assertRaises(ManifestNotFoundError):
                load_captain_manifest(start=project)

    def test_rejects_removed_packaging_contract(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_manifest(
                project,
                packaging={
                    "stager": {"target": "linux"},
                    "embark": {"formats": ["deb"]},
                },
            )
            with self.assertRaisesRegex(ManifestError, "packaging"):
                load_captain_manifest(start=project)


if __name__ == "__main__":
    unittest.main()
