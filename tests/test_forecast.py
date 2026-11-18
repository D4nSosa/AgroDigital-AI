import unittest
from agrodigital.forecast import detect_monthly_anomalies, forecast_monthly_series, FORECAST_LABEL


def seasonal_series():
    rows = []
    seasonal = [0, 2, 4, 6, 4, 2, 0, -2, -4, -6, -4, -2]
    for year in range(2021, 2024):
        for month in range(1, 13):
            index = (year - 2021) * 12 + month - 1
            rows.append({"date": f"{year}-{month:02d}-01", "value": 50 + 0.5 * index + seasonal[month - 1]})
    return rows


class ForecastTests(unittest.TestCase):
    def test_forecast_recovers_known_linear_trend_and_seasonality(self):
        result = forecast_monthly_series(seasonal_series(), periods=3)
        self.assertEqual(result["classification"], FORECAST_LABEL)
        self.assertAlmostEqual(result["trend_per_month"], 0.5, places=6)
        self.assertEqual(len(result["forecasts"]), 3)
        self.assertLess(result["forecasts"][0]["lower_bound"], result["forecasts"][0]["forecast_value"])
        self.assertGreater(result["forecasts"][0]["upper_bound"], result["forecasts"][0]["forecast_value"])

    def test_anomaly_detection_flags_large_monthly_departure(self):
        rows = seasonal_series()
        rows[-1]["value"] += 100
        result = detect_monthly_anomalies(rows)
        self.assertTrue(result["anomalies"][-1]["is_anomaly"])

    def test_rejects_short_series_and_nonfinite_values(self):
        with self.assertRaises(ValueError):
            forecast_monthly_series([{"date": "2024-01-01", "value": 1}] * 6)
        rows = seasonal_series()
        rows[0]["value"] = float("nan")
        with self.assertRaises(ValueError):
            forecast_monthly_series(rows)


if __name__ == "__main__":
    unittest.main()
