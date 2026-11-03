import unittest

from agrodigital.agent_tools import plan_analysis, calculate_gdd, calculate_rainfall


class AgentToolTests(unittest.TestCase):
    def test_plan_marks_missing_aoi_and_evidence(self):
        result = plan_analysis("Assess crop suitability")
        self.assertEqual(result["status"], "plan_only")
        self.assertEqual(result["aoi_status"], "missing")
        self.assertTrue(any("AOI" in item for item in result["missing_or_uncertain"]))
        self.assertIn("No geospatial processing", result["execution"])

    def test_plan_validates_bbox(self):
        with self.assertRaises(ValueError):
            plan_analysis("Assess", bbox=[1, 2, 0, 3])

    def test_calculations(self):
        self.assertEqual(calculate_gdd(12, 28, 10)["gdd_degree_days"], 10.0)
        self.assertEqual(calculate_rainfall([12.5, 0, 8])["rainfall_total_mm"], 20.5)


if __name__ == "__main__":
    unittest.main()
