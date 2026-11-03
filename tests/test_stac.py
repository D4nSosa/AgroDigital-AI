import json
import unittest
from unittest.mock import patch
from agrodigital.stac import search_stac, get_stac_item


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class STACTests(unittest.TestCase):
    def test_rejects_invalid_area_and_endpoint(self):
        with self.assertRaises(ValueError):
            search_stac(bbox=[-200, -90, 10, 90])
        with self.assertRaises(ValueError):
            search_stac(bbox=[-1, -1, 1, 1], endpoint="http://example.com")

    @patch("agrodigital.stac.urlopen")
    def test_returns_catalog_metadata_and_asset_details(self, mocked):
        mocked.return_value = FakeResponse({"features": [{
            "id": "scene-1", "collection": "sentinel-2-l2a",
            "properties": {"datetime": "2026-01-15T10:00:00Z", "eo:cloud_cover": 12.5},
            "bbox": [-1, -1, 1, 1],
            "assets": {"red": {"href": "https://example.com/red.tif",
                               "raster:bands": [{"scale": 0.0001}]}}
        }], "links": []})
        result = search_stac(bbox=[-1, -1, 1, 1], max_items=5)
        self.assertEqual(result["returned_items"], 1)
        self.assertEqual(result["items"][0]["id"], "scene-1")
        self.assertEqual(result["items"][0]["cloud_cover_percent"], 12.5)
        self.assertIn("red", result["items"][0]["asset_details"])
        self.assertIn("metadata only", result["note"])

    @patch("agrodigital.stac.urlopen")
    def test_fetches_full_stac_item(self, mocked):
        item = {"id": "scene-1", "assets": {"red": {"href": "https://example.com/red.tif"}}}
        mocked.return_value = FakeResponse(item)
        result = get_stac_item("scene-1")
        self.assertEqual(result["id"], "scene-1")
        self.assertIn("red", result["assets"])


if __name__ == "__main__":
    unittest.main()
