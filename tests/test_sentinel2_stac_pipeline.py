import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_origin

from agrodigital.sentinel2_stac import process_sentinel2_stac_item


class Sentinel2STACPipelineTests(unittest.TestCase):
    def test_downloads_assets_aligns_scl_and_writes_ndvi(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = {
                "driver": "GTiff", "width": 2, "height": 2, "count": 1,
                "dtype": "uint16", "crs": "EPSG:32621",
                "transform": from_origin(500000, 7000000, 10, 10),
            }
            item = {
                "id": "synthetic-scene",
                "collection": "sentinel-2-l2a",
                "bbox": [-57, -28, -56, -27],
                "properties": {
                    "datetime": "2026-01-15T10:00:00Z",
                    "eo:cloud_cover": 5.0,
                    "earthsearch:boa_offset_applied": True,
                },
                "links": [{"rel": "license", "href": "https://example.test/license"}],
                "assets": {
                    "red": {"href": "https://example.test/red.tif",
                            "raster:bands": [{"scale": 0.0001}]},
                    "nir": {"href": "https://example.test/nir.tif",
                            "raster:bands": [{"scale": 0.0001}]},
                    "scl": {"href": "https://example.test/scl.tif"},
                },
            }

            def fake_download(url, destination, **kwargs):
                destination = Path(destination)
                if destination.name.endswith("_red.tif"):
                    with rasterio.open(destination, "w", **profile) as dst:
                        dst.write(np.full((2, 2), 2000, dtype="uint16"), 1)
                elif destination.name.endswith("_nir.tif"):
                    with rasterio.open(destination, "w", **profile) as dst:
                        dst.write(np.full((2, 2), 6000, dtype="uint16"), 1)
                else:
                    coarse = dict(profile)
                    coarse.update(width=1, height=1,
                                  transform=from_origin(500000, 7000000, 20, 20))
                    with rasterio.open(destination, "w", **coarse) as dst:
                        dst.write(np.array([[4]], dtype="uint16"), 1)
                return {"path": str(destination), "bytes": destination.stat().st_size,
                        "sha256": "synthetic", "url": url, "verified_checksum": False}

            with patch("agrodigital.sentinel2_stac.get_stac_item", return_value=item), \
                 patch("agrodigital.sentinel2_stac.download_asset", side_effect=fake_download):
                result = process_sentinel2_stac_item(
                    "synthetic-scene", root / "out", use_scl=True
                )

            self.assertEqual(result["status"], "processed")
            self.assertTrue(result["scl_aligned_path"])
            self.assertTrue(Path(result["processing"]["output"]).exists())
            with rasterio.open(result["processing"]["output"]) as src:
                self.assertEqual((src.width, src.height), (2, 2))
                self.assertTrue(np.allclose(src.read(1), 0.5))
            self.assertEqual(result["item"]["datetime"], "2026-01-15T10:00:00Z")


if __name__ == "__main__":
    unittest.main()
