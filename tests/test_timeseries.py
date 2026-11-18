import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_origin

from agrodigital.timeseries import summarize_sentinel2_timeseries


class Sentinel2TimeSeriesTests(unittest.TestCase):
    def test_per_scene_stats_and_temporal_median(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = {"driver": "GTiff", "width": 2, "height": 2, "count": 1,
                       "dtype": "float32", "crs": "EPSG:4326",
                       "transform": from_origin(-57.95, -28.13, 0.01, 0.01),
                       "nodata": -9999.0}
            for name, value in (("one.tif", 0.2), ("two.tif", 0.6)):
                with rasterio.open(root / name, "w", **profile) as dst:
                    dst.write(np.full((2, 2), value, dtype="float32"), 1)
            aoi = {"type": "Polygon", "coordinates": [[[-57.95, -28.13], [-57.93, -28.13],
                    [-57.93, -28.15], [-57.95, -28.15], [-57.95, -28.13]]]}
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": temp}):
                result = summarize_sentinel2_timeseries(
                    [{"date": "2024-01-01", "path": "one.tif"},
                     {"date": "2024-02-01", "path": "two.tif"}], aoi)
            self.assertEqual(result["scene_count"], 2)
            self.assertEqual(result["scenes"][0]["valid_pixels"], 4)
            with rasterio.open(root / "sentinel2_ndvi_median_composite.tif") as src:
                self.assertTrue(np.allclose(src.read(1), 0.4))
            self.assertTrue((root / "sentinel2_timeseries.csv").exists())


if __name__ == "__main__":
    unittest.main()
