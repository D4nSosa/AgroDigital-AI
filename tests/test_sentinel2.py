import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if importlib.util.find_spec("rasterio") and importlib.util.find_spec("numpy"):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    from agrodigital.sentinel2 import calculate_sentinel2_ndvi, Sentinel2Error
    from agrodigital.paths import WorkdirError
    from agrodigital.sentinel2_stac import _align_scl_to_red_grid
    AVAILABLE = True
else:
    AVAILABLE = False


@unittest.skipUnless(AVAILABLE, "Install agrodigital-ai[raster] to run Sentinel-2 tests")
class Sentinel2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.profile = {"driver": "GTiff", "width": 2, "height": 2, "count": 1,
                        "dtype": "uint16", "crs": "EPSG:32621",
                        "transform": from_origin(500000, 7000000, 10, 10)}
        self.red, self.nir, self.scl = [self.root / name for name in ("red.tif", "nir.tif", "scl.tif")]
        with rasterio.open(self.red, "w", **self.profile) as dst:
            dst.write(np.array([[2000, 2000], [2000, 2000]], dtype="uint16"), 1)
        with rasterio.open(self.nir, "w", **self.profile) as dst:
            dst.write(np.array([[6000, 6000], [6000, 6000]], dtype="uint16"), 1)
        with rasterio.open(self.scl, "w", **self.profile) as dst:
            dst.write(np.array([[2, 9], [6, 7]], dtype="uint16"), 1)

    def tearDown(self): self.temp.cleanup()

    def test_ndvi_and_scl_mask(self):
        output = self.root / "ndvi.tif"
        with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
            result = calculate_sentinel2_ndvi("red.tif", "nir.tif", "ndvi.tif",
                                              scale_factor=10000, scl_path="scl.tif")
        self.assertTrue(result["scl_applied"])
        with rasterio.open(output) as src:
            values = src.read(1)
            self.assertAlmostEqual(float(values[0, 0]), 0.5, places=6)
            self.assertEqual(float(values[0, 1]), -9999.0)
            self.assertAlmostEqual(float(values[1, 0]), 0.5, places=6)
            self.assertAlmostEqual(float(values[1, 1]), 0.5, places=6)

    def test_custom_scl_exclusion_list_overrides_defaults(self):
        with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
            calculate_sentinel2_ndvi("red.tif", "nir.tif", "custom-mask.tif",
                                     scale_factor=10000, scl_path="scl.tif",
                                     excluded_scl_classes=(2,))
        with rasterio.open(self.root / "custom-mask.tif") as src:
            values = src.read(1)
            self.assertEqual(float(values[0, 0]), -9999.0)
            self.assertAlmostEqual(float(values[0, 1]), 0.5, places=6)
            self.assertAlmostEqual(float(values[1, 0]), 0.5, places=6)
            self.assertAlmostEqual(float(values[1, 1]), 0.5, places=6)

    def test_supports_independent_band_scale_factors(self):
        output = self.root / "different-scale.tif"
        with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
            calculate_sentinel2_ndvi("red.tif", "nir.tif", "different-scale.tif",
                                     scale_factor=10000, nir_scale_factor=20000)
        with rasterio.open(output) as src:
            self.assertAlmostEqual(float(src.read(1)[0, 0]), 0.2, places=6)

    def test_aligns_20m_scl_to_10m_red_grid(self):
        coarse = self.root / "coarse-scl.tif"
        profile = dict(self.profile)
        profile.update(width=1, height=1, transform=from_origin(500000, 7000000, 20, 20))
        with rasterio.open(coarse, "w", **profile) as dst:
            dst.write(np.array([[4]], dtype="uint16"), 1)
        aligned = self.root / "aligned-scl.tif"
        result_path = _align_scl_to_red_grid(coarse, self.red, aligned)
        with rasterio.open(result_path) as src:
            self.assertEqual((src.width, src.height), (2, 2))
            self.assertTrue(np.all(src.read(1) == 4))

    def test_rejects_absolute_output_path(self):
        with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
            with self.assertRaises(WorkdirError):
                calculate_sentinel2_ndvi("red.tif", "nir.tif", str(self.root / "outside.tif"), scale_factor=10000)

    def test_rejects_invalid_scale(self):
        with self.assertRaises(Sentinel2Error):
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
                calculate_sentinel2_ndvi("red.tif", "nir.tif", "bad.tif", scale_factor=0)

    def test_rejects_unaligned_bands(self):
        shifted = self.root / "shifted.tif"
        profile = dict(self.profile)
        profile["transform"] = from_origin(500010, 7000000, 10, 10)
        with rasterio.open(shifted, "w", **profile) as dst:
            dst.write(np.ones((2, 2), dtype="uint16"), 1)
        with self.assertRaises(Sentinel2Error):
            with patch.dict(os.environ, {"AGRODIGITAL_WORKDIR": str(self.root)}):
                calculate_sentinel2_ndvi("red.tif", "shifted.tif", "bad.tif", scale_factor=10000)


if __name__ == "__main__": unittest.main()
