"""Regression tests for the portable Skill utilities; fixtures are synthetic and local."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "agrodigital-ai" / "scripts"

class SkillScriptTests(unittest.TestCase):
    def run_script(self, name, *args, expect=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, expect, result.stderr)
        return result

    def test_geojson_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.geojson"
            bad = Path(tmp) / "bad.geojson"
            good.write_text(json.dumps({"type":"FeatureCollection","features":[
                {"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-56.0,-27.0]}}
            ]}))
            bad.write_text(json.dumps({"type":"Point","coordinates":[250,0]}))
            result = json.loads(self.run_script("validate_geojson.py", good).stdout)
            self.assertTrue(result["valid_structure"])
            self.run_script("validate_geojson.py", bad, expect=2)

    def test_indices_from_supplied_band_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/"bands.csv", Path(tmp)/"indices.csv"
            src.write_text("nir,red,green\n0.8,0.2,0.4\n")
            self.run_script("calculate_indices.py", src, "-o", dst, "--ndwi")
            with dst.open() as f:
                row = next(csv.DictReader(f))
            self.assertAlmostEqual(float(row["ndvi"]), 0.6)
            self.assertAlmostEqual(float(row["ndwi_mcfeeters"]), -1/3, places=6)

    def test_gdd_cumulative(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/"temps.csv", Path(tmp)/"gdd.csv"
            src.write_text("tmin_c,tmax_c\n10,20\n5,15\n")
            result = json.loads(self.run_script("calculate_gdd.py", src, "-o", dst, "--base", 10).stdout)
            self.assertAlmostEqual(result["cumulative_gdd_c_day"], 5.0)

    def test_timeseries_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/"series.csv", Path(tmp)/"chart.svg"
            src.write_text("date,ndvi\n2025-01-01,0.2\n2025-02-01,0.6\n2025-03-01,0.4\n")
            result = json.loads(self.run_script("plot_timeseries.py", src, "--value", "ndvi",
                                                "--label", "NDVI", "-o", dst).stdout)
            self.assertEqual(result["observations"], 3)
            self.assertIn("<svg", dst.read_text())

if __name__ == "__main__":
    unittest.main()
