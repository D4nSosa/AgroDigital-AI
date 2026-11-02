import math, unittest
from agrodigital.indices import ndvi, ndwi, normalized_difference

class IndexTests(unittest.TestCase):
    def test_ndvi_scalar(self): self.assertAlmostEqual(ndvi(0.8,0.2),0.6)
    def test_ndwi_sequence(self):
        result=ndwi([0.4,0.2],[0.2,0.2])
        self.assertAlmostEqual(float(result[0]),1/3); self.assertAlmostEqual(float(result[1]),0.0)
    def test_zero_denominator(self): self.assertTrue(math.isnan(normalized_difference(0,0)))

if __name__ == "__main__": unittest.main()
