# AgroDigital-AI — Google Colab time-series workflow
# Run in a Colab notebook. Edit PARAMETERS before executing.
# Free public data sources; Earth Engine requires the user's own authenticated
# Google account and accepted Earth Engine terms. NASA POWER uses public HTTP API.

# ---- PARAMETERS (edit these first) ----
AOI_COORDS = [
    [-57.95, -28.15], [-57.93, -28.15], [-57.93, -28.13],
    [-57.95, -28.13], [-57.95, -28.15]
]
START_DATE = "2020-01-01"
END_DATE = "2025-12-31"
CLOUD_PERCENT_MAX = 80
EXPORT_PREFIX = "agrodigital"
SCALE_S2_M = 10
SCALE_LANDSAT_M = 30

# ---- Setup ----
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "earthengine-api", "pandas", "matplotlib"])

import ee
import json
import urllib.parse
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

aoi = ee.Geometry.Polygon([AOI_COORDS])
start = pd.Timestamp(START_DATE)
end = pd.Timestamp(END_DATE)
months = pd.date_range(start=start.to_period("M").start_time,
                       end=end.to_period("M").start_time, freq="MS")


def monthly_reduce(collection, band, scale, reducer="mean"):
    """Reduce one image per calendar month over the polygon; returns actual source dates."""
    rows = []
    for month_start in months:
        month_end = month_start + pd.offsets.MonthBegin(1)
        subset = collection.filterDate(month_start.strftime("%Y-%m-%d"),
                                       month_end.strftime("%Y-%m-%d"))
        count = subset.size().getInfo()
        if not count:
            continue
        image = subset.median().select(band) if reducer == "median" else subset.mean().select(band)
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean().combine(ee.Reducer.median(), sharedInputs=True)
                    .combine(ee.Reducer.percentile([10, 90]), sharedInputs=True)
                    .combine(ee.Reducer.count(), sharedInputs=True),
            geometry=aoi, scale=scale, maxPixels=1e9, tileScale=4
        ).getInfo()
        rows.append({"date": month_start.date().isoformat(), "source_image_count": count, **stats})
    return pd.DataFrame(rows)


# Sentinel-2 L2A monthly median NDVI.
def mask_s2(image):
    scl = image.select("SCL")
    # Exclude 0, 1, 3, 8, 9, 10, 11; retain 2, 6 and 7 by default.
    mask = (scl.neq(0).And(scl.neq(1)).And(scl.neq(3)).And(scl.neq(8))
            .And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11)))
    return image.updateMask(mask).addBands(
        image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    )

s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(aoi).filterDate(START_DATE, END_DATE)
      .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", CLOUD_PERCENT_MAX))
      .map(mask_s2))
s2_monthly = monthly_reduce(s2, "NDVI", SCALE_S2_M, reducer="median")
s2_monthly.to_csv(f"{EXPORT_PREFIX}_sentinel2_ndvi.csv", index=False)


# Landsat 8/9 Collection 2 Level-2; QA_PIXEL bits 1-5 exclude dilated cloud,
# cirrus, cloud, cloud shadow and snow. SR scale = 0.0000275, offset = -0.2.
def landsat_ndvi(image):
    qa = image.select("QA_PIXEL")
    mask = (qa.bitwiseAnd(1 << 1).eq(0).And(qa.bitwiseAnd(1 << 2).eq(0))
            .And(qa.bitwiseAnd(1 << 3).eq(0)).And(qa.bitwiseAnd(1 << 4).eq(0))
            .And(qa.bitwiseAnd(1 << 5).eq(0)))
    red = image.select("SR_B4").multiply(0.0000275).add(-0.2)
    nir = image.select("SR_B5").multiply(0.0000275).add(-0.2)
    return nir.subtract(red).divide(nir.add(red)).rename("NDVI").updateMask(mask)

landsat = (ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
           .merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"))
           .filterBounds(aoi).filterDate(START_DATE, END_DATE).map(landsat_ndvi))
landsat_monthly = monthly_reduce(landsat, "NDVI", SCALE_LANDSAT_M, reducer="median")
landsat_monthly.to_csv(f"{EXPORT_PREFIX}_landsat_ndvi.csv", index=False)


# CHIRPS monthly precipitation sum (mm/month).
chirps = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
          .filterBounds(aoi).filterDate(START_DATE, END_DATE))
chirps_rows = []
for month_start in months:
    month_end = month_start + pd.offsets.MonthBegin(1)
    subset = chirps.filterDate(month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
    if subset.size().getInfo():
        image = subset.sum().rename("precip_mm")
        value = image.reduceRegion(ee.Reducer.mean(), aoi, 5500, maxPixels=1e9).getInfo()
        chirps_rows.append({"date": month_start.date().isoformat(), "precip_mm_mean": value.get("precip_mm")})
chirps_monthly = pd.DataFrame(chirps_rows)
chirps_monthly.to_csv(f"{EXPORT_PREFIX}_chirps_monthly.csv", index=False)


# ERA5-Land daily aggregates: monthly mean 2 m temperature (°C) and
# monthly accumulated total precipitation (mm). Reanalysis, not a station.
era5 = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
        .filterBounds(aoi).filterDate(START_DATE, END_DATE)
        .map(lambda image: image.addBands(
            image.select("temperature_2m").subtract(273.15).rename("t2m_c")
        ).addBands(image.select("total_precipitation_sum").multiply(1000).rename("precip_mm"))))
era5_temp_rows, era5_rain_rows = [], []
for month_start in months:
    month_end = month_start + pd.offsets.MonthBegin(1)
    subset = era5.filterDate(month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
    if subset.size().getInfo():
        temp = subset.select("t2m_c").mean().reduceRegion(ee.Reducer.mean(), aoi, 11000, maxPixels=1e9).getInfo()
        rain = subset.select("precip_mm").sum().reduceRegion(ee.Reducer.mean(), aoi, 11000, maxPixels=1e9).getInfo()
        era5_temp_rows.append({"date": month_start.date().isoformat(), "t2m_c_mean": temp.get("t2m_c")})
        era5_rain_rows.append({"date": month_start.date().isoformat(), "precip_mm_sum": rain.get("precip_mm")})
era5_temp = pd.DataFrame(era5_temp_rows)
era5_rain = pd.DataFrame(era5_rain_rows)
era5_temp.to_csv(f"{EXPORT_PREFIX}_era5_temperature.csv", index=False)
era5_rain.to_csv(f"{EXPORT_PREFIX}_era5_precipitation.csv", index=False)


# NASA POWER monthly point data at AOI centroid. This is a gridded point value,
# not a polygon average or local weather-station observation.
centroid = aoi.centroid(1).coordinates().getInfo()
lon, lat = centroid[0], centroid[1]
params = {
    "parameters": "T2M,PRECTOTCORR", "community": "AG",
    "longitude": lon, "latitude": lat,
    "start": START_DATE[:4], "end": END_DATE[:4], "format": "JSON"
}
power_url = "https://power.larc.nasa.gov/api/temporal/monthly/point?" + urllib.parse.urlencode(params)
with urllib.request.urlopen(power_url, timeout=60) as response:
    power_json = json.loads(response.read().decode("utf-8"))
power = power_json["properties"]["parameter"]
power_rows = []
for key, temp in power["T2M"].items():
    if key.isdigit() and len(key) == 6:
        rain = power["PRECTOTCORR"].get(key)
        power_rows.append({"month": key, "date": f"{key[:4]}-{key[4:]}-01",
                           "temperature_c": temp, "precipitation_mm_day": rain})
power_df = pd.DataFrame(power_rows)
power_df.to_csv(f"{EXPORT_PREFIX}_nasa_power_monthly.csv", index=False)


# Basic charts from the exported tables.
for frame, column, title, ylabel in [
    (s2_monthly, "NDVI_median", "Sentinel-2 monthly median NDVI", "NDVI"),
    (landsat_monthly, "NDVI_median", "Landsat monthly median NDVI", "NDVI"),
    (chirps_monthly, "precip_mm_mean", "CHIRPS monthly precipitation sum", "mm/month"),
    (era5_temp, "t2m_c_mean", "ERA5-Land monthly mean temperature", "°C"),
]:
    if not frame.empty and column in frame:
        plt.figure(figsize=(12, 4))
        plt.plot(pd.to_datetime(frame["date"]), frame[column])
        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

print("CSV files written to the Colab working directory. Download them from the Files panel.")
print("NASA POWER point coordinates (AOI centroid):", lat, lon)
print("All weather products are gridded datasets; ERA5-Land and NASA POWER are not station measurements.")
