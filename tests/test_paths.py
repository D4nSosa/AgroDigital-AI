import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agrodigital.paths import WorkdirError, resolve_work_path


class WorkPathTests(unittest.TestCase):
    def test_relative_path_is_confined(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": tmp}):
                result = resolve_work_path("outputs/result.tif", create_parent=True)
                self.assertEqual(result.parent, Path(tmp) / "outputs")
                self.assertTrue(result.parent.is_dir())

    def test_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": tmp}):
                with self.assertRaises(WorkdirError):
                    resolve_work_path("../outside.tif")

    def test_rejects_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": tmp}):
                with self.assertRaises(WorkdirError):
                    resolve_work_path(str(Path(tmp) / "inside.tif"))

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "work"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "link").symlink_to(outside, target_is_directory=True)
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(root)}):
                with self.assertRaises(WorkdirError):
                    resolve_work_path("link/file.tif")


if __name__ == "__main__":
    unittest.main()
