import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

if importlib.util.find_spec("rasterio") and importlib.util.find_spec("numpy"):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    from agrodigital.raster import calculate_normalized_difference, clip_raster, inspect_raster, reproject_raster
    RASTER_AVAILABLE = True
else:
    RASTER_AVAILABLE = False


@unittest.skipUnless(RASTER_AVAILABLE, "Install agrodigital-ai[raster] to run raster tests")
class RasterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.tif"
        profile = {"driver": "GTiff", "width": 4, "height": 4, "count": 2,
                   "dtype": "float32", "crs": "EPSG:4326",
                   "transform": from_origin(-1, 1, 0.1, 0.1), "nodata": -9999.0}
        with rasterio.open(self.source, "w", **profile) as dst:
            dst.write(np.array([[3, 1, 0, 2], [3, 1, 2, 2], [1, 3, 2, 2], [1, 3, 2, 2]], dtype="float32"), 1)
            dst.write(np.array([[1, 3, 0, 2], [1, 3, 2, 2], [3, 1, 2, 2], [3, 1, 2, 2]], dtype="float32"), 2)

    def tearDown(self):
        self.temp.cleanup()

    def test_inspect_metadata(self):
        result = inspect_raster(self.source)
        self.assertEqual(result["width"], 4)
        self.assertEqual(result["band_count"], 2)
        self.assertEqual(result["crs"], "EPSG:4326")

    def test_normalized_difference_output(self):
        output = self.root / "index.tif"
        calculate_normalized_difference(self.source, output, 1, 2, label="test-index")
        with rasterio.open(output) as ds:
            values = ds.read(1)
            self.assertAlmostEqual(float(values[0, 0]), 0.5)
            self.assertAlmostEqual(float(values[0, 1]), -0.5)
            self.assertEqual(float(values[0, 2]), -9999.0)
            self.assertEqual(ds.tags(1)["input_bands"], "1,2")

    def test_clip_and_reproject(self):
        aoi = self.root / "aoi.geojson"
        aoi.write_text(json.dumps({"type": "Polygon", "coordinates": [[[-1, 0.8], [-0.8, 0.8], [-0.8, 1], [-1, 1], [-1, 0.8]]]}))
        clipped = self.root / "clip.tif"
        result = clip_raster(self.source, aoi, clipped)
        self.assertEqual(result["width"], 2)
        projected = self.root / "projected.tif"
        result = reproject_raster(clipped, projected, "EPSG:3857")
        self.assertEqual(result["target_crs"], "EPSG:3857")
        self.assertGreater(result["width"], 0)


if __name__ == "__main__":
    unittest.main()
