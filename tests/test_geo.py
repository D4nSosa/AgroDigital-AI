import unittest
from agrodigital.geo import GeoJSONError, validate_geojson

class GeoJSONTests(unittest.TestCase):
    def test_valid_polygon_feature_collection(self):
        data={"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[1,1],[2,1],[2,2],[1,2],[1,1]]]}}]}
        result=validate_geojson(data)
        self.assertTrue(result["valid"]); self.assertEqual(result["coordinate_count"],5)
    def test_rejects_out_of_range_longitude(self):
        with self.assertRaises(GeoJSONError): validate_geojson({"type":"Point","coordinates":[181,0]})
    def test_rejects_unclosed_polygon(self):
        with self.assertRaises(GeoJSONError): validate_geojson({"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1]]]})

if __name__ == "__main__": unittest.main()
