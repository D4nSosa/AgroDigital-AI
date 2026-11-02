import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

if importlib.util.find_spec("pyproj") and importlib.util.find_spec("shapely"):
    from agrodigital.vector import reproject_geojson, validate_topology
    VECTOR_AVAILABLE = True
else:
    VECTOR_AVAILABLE = False


@unittest.skipUnless(VECTOR_AVAILABLE, "Install agrodigital-ai[geo] to run vector tests")
class VectorTests(unittest.TestCase):
    def test_reproject_and_validate(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.geojson"
            target = Path(folder) / "target.geojson"
            source.write_text(json.dumps({"type": "Feature", "properties": {},
                "geometry": {"type": "Point", "coordinates": [111319.49079327357, 0]}}))
            result = reproject_geojson(source, target, "EPSG:3857", "EPSG:4326")
            output = json.loads(target.read_text())
            self.assertEqual(result["target_crs"], "EPSG:4326")
            self.assertEqual(output["agrodigital:coordinate_reference_system"], "EPSG:4326")
            self.assertAlmostEqual(output["geometry"]["coordinates"][0], 1.0, places=5)
            self.assertTrue(validate_topology(target)["valid"])


if __name__ == "__main__":
    unittest.main()
