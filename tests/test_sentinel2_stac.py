import unittest

from agrodigital.sentinel2_stac import _reflectance_parameters, _asset_href, Sentinel2STACError


class Sentinel2STACTests(unittest.TestCase):
    def test_earth_search_harmonized_offset(self):
        item = {
            "properties": {"earthsearch:boa_offset_applied": True},
            "assets": {"red": {"raster:bands": [{"scale": 0.0001, "offset": -0.1}]}}
        }
        result = _reflectance_parameters(item, "red")
        self.assertEqual(result["scale_factor"], 10000)
        self.assertEqual(result["offset"], 0.0)

    def test_earth_search_unharmonized_offset(self):
        item = {
            "properties": {"earthsearch:boa_offset_applied": False},
            "assets": {"nir": {"raster:bands": [{"scale": 0.0001}]}}
        }
        self.assertAlmostEqual(_reflectance_parameters(item, "nir")["offset"], -0.1)

    def test_baseline_offset_fallback(self):
        item = {
            "properties": {"s2:processing_baseline": "05.00"},
            "assets": {"red": {"raster:bands": [{"scale": 0.0001}]}}
        }
        self.assertAlmostEqual(_reflectance_parameters(item, "red")["offset"], -0.1)

    def test_generic_raster_offset(self):
        item = {"properties": {}, "assets": {"red": {"raster:bands": [{"scale": 0.0002, "offset": -0.03}]}}}
        self.assertAlmostEqual(_reflectance_parameters(item, "red")["scale_factor"], 5000)
        self.assertAlmostEqual(_reflectance_parameters(item, "red")["offset"], -0.03)

    def test_reject_non_https_asset(self):
        with self.assertRaises(Sentinel2STACError):
            _asset_href({"assets": {"red": {"href": "http://example.com/red.tif"}}}, "red")


if __name__ == "__main__":
    unittest.main()
