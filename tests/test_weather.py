import unittest
from agrodigital.weather import growing_degree_days, rainfall_total

class WeatherTests(unittest.TestCase):
    def test_gdd(self): self.assertEqual(growing_degree_days(12,28,10),10)
    def test_gdd_upper_cap(self): self.assertEqual(growing_degree_days(20,40,10,upper_c=30),20)
    def test_reversed_temperatures(self):
        with self.assertRaises(ValueError): growing_degree_days(25,20,10)
    def test_rainfall(self): self.assertAlmostEqual(rainfall_total([12.5,0,8,3.2]),23.7)
    def test_missing_rainfall_explicit(self):
        with self.assertRaises(ValueError): rainfall_total([2,None,3])
        self.assertEqual(rainfall_total([2,None,3],ignore_missing=True),5)

if __name__ == "__main__": unittest.main()
