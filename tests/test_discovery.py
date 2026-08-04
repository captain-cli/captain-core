import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from captain_core.discovery import find_captain_root, find_project_root
from captain_core.errors import CaptainProjectNotFoundError


class DiscoveryTests(unittest.TestCase):
    def test_finds_project_root_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "captain").mkdir()
            nested = root / "apps" / "desktop" / "src"
            nested.mkdir(parents=True)
            self.assertEqual(find_project_root(nested), root.resolve())

    def test_uses_captain_root_environment_override(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            captain_root = Path(temporary_directory) / "captain"
            captain_root.mkdir()
            with patch.dict(os.environ, {"CAPTAIN_ROOT": str(captain_root)}):
                self.assertEqual(find_captain_root(), captain_root.resolve())

    def test_raises_when_project_is_missing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(CaptainProjectNotFoundError):
                find_project_root(temporary_directory)


if __name__ == "__main__":
    unittest.main()
