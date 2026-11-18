import tomllib
import unittest
from pathlib import Path

import agrodigital


class PackageVersionTests(unittest.TestCase):
    """Regression guard for the single package-version source of truth."""
    def test_package_and_build_metadata_versions_match(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        self.assertEqual(agrodigital.__version__, metadata["project"]["version"])


if __name__ == "__main__":
    unittest.main()
