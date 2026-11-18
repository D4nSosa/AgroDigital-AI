// AgroDigital-AI — Google Earth Engine Code Editor
// EDIT THESE PARAMETERS FIRST. Geometry coordinates must be WGS84 [lon, lat].
// This script creates per-image AOI means and Drive CSV exports; it does not
// produce field yield or plant-health measurements.

var AOI = ee.Geometry.Polygon([
  [[-57.95, -28.15], [-57.93, -28.15], [-57.93, -28.13],
   [-57.95, -28.13], [-57.95, -28.15]]
]);
var START_DATE = '2020-01-01';
var END_DATE = '2025-12-31';
var CLOUD_PERCENT_MAX = 80;
var SCALE_OPTICAL_M = 30;   // use 10 for Sentinel-2; 30 for Landsat/weather
var EXPORT_FOLDER = 'AgroDigitalAI';

Map.centerObject(AOI, 13);
Map.addLayer(AOI, {color: 'yellow'}, 'AOI');

// Sentinel-2 L2A: exclude SCL 0, 1, 3, 8, 9, 10, 11.
// SCL 2, 6 and 7 are retained by default.
function maskS2(image) {
  var scl = image.select('SCL');
  var mask = scl.neq(0).and(scl.neq(1)).and(scl.neq(3))
    .and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  return image.updateMask(mask)
    .addBands(image.normalizedDifference(['B8', 'B4']).rename('NDVI'))
    .copyProperties(image, ['system:time_start', 'CLOUDY_PIXEL_PERCENTAGE']);
}

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(AOI).filterDate(START_DATE, END_DATE)
  .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_PERCENT_MAX))
  .map(maskS2);

function landsatNdvi(image) {
  // Landsat Collection 2 Level-2 QA_PIXEL bits: dilated cloud, cirrus,
  // cloud, cloud shadow and snow are excluded.
  var qa = image.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 1).eq(0)
    .and(qa.bitwiseAnd(1 << 2).eq(0))
    .and(qa.bitwiseAnd(1 << 3).eq(0))
    .and(qa.bitwiseAnd(1 << 4).eq(0))
    .and(qa.bitwiseAnd(1 << 5).eq(0));
  var red = image.select('SR_B4').multiply(0.0000275).add(-0.2);
  var nir = image.select('SR_B5').multiply(0.0000275).add(-0.2);
  return nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    .updateMask(mask).copyProperties(image, ['system:time_start']);
}

var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'))
  .filterBounds(AOI).filterDate(START_DATE, END_DATE)
  .map(landsatNdvi);

function addAoiStats(collection, band, scale, sensor) {
  return ee.FeatureCollection(collection.map(function(image) {
    var stats = image.select(band).reduceRegion({
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.median(), sharedInputs: true
      }).combine({reducer2: ee.Reducer.percentile([10, 90]), sharedInputs: true})
       .combine({reducer2: ee.Reducer.count(), sharedInputs: true}),
      geometry: AOI, scale: scale, maxPixels: 1e9, tileScale: 4
    });
    return ee.Feature(null, stats).set({
      date: ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'),
      timestamp: image.get('system:time_start'), sensor: sensor
    });
  })).sort('timestamp');
}

var s2Table = addAoiStats(s2, 'NDVI', 10, 'Sentinel-2 L2A');
var landsatTable = addAoiStats(landsat, 'NDVI', 30, 'Landsat 8/9 C2 L2');

var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
  .filterBounds(AOI).filterDate(START_DATE, END_DATE);
var chirpsTable = addAoiStats(chirps, 'precipitation', 5500, 'CHIRPS daily mm');

var era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')
  .filterBounds(AOI).filterDate(START_DATE, END_DATE)
  .map(function(image) {
    return image.addBands(image.select('temperature_2m').subtract(273.15).rename('t2m_c'))
      .addBands(image.select('total_precipitation_sum').multiply(1000).rename('precip_mm'));
  });
var era5TempTable = addAoiStats(era5, 't2m_c', 11000, 'ERA5-Land daily temperature C');
var era5RainTable = addAoiStats(era5, 'precip_mm', 11000, 'ERA5-Land daily precipitation mm');

print('Sentinel-2 NDVI AOI statistics', s2Table.limit(10));
print('Landsat NDVI AOI statistics', landsatTable.limit(10));
print('CHIRPS precipitation AOI statistics', chirpsTable.limit(10));
print('ERA5-Land temperature AOI statistics', era5TempTable.limit(10));
print('ERA5-Land precipitation AOI statistics', era5RainTable.limit(10));

print(ui.Chart.feature.byFeature(s2Table, 'date', ['NDVI_mean'])
  .setOptions({title: 'Sentinel-2 AOI mean NDVI', hAxis: {title: 'Date'}, vAxis: {title: 'NDVI'}}));
print(ui.Chart.feature.byFeature(landsatTable, 'date', ['NDVI_mean'])
  .setOptions({title: 'Landsat AOI mean NDVI', hAxis: {title: 'Date'}, vAxis: {title: 'NDVI'}}));
print(ui.Chart.feature.byFeature(chirpsTable, 'date', ['precipitation_mean'])
  .setOptions({title: 'CHIRPS daily AOI mean precipitation', hAxis: {title: 'Date'}, vAxis: {title: 'mm/day'}}));
print(ui.Chart.feature.byFeature(era5TempTable, 'date', ['t2m_c_mean'])
  .setOptions({title: 'ERA5-Land daily AOI mean temperature', hAxis: {title: 'Date'}, vAxis: {title: '°C'}}));

Export.table.toDrive({collection: s2Table, description: 'AgroDigital_Sentinel2_NDVI', folder: EXPORT_FOLDER, fileFormat: 'CSV'});
Export.table.toDrive({collection: landsatTable, description: 'AgroDigital_Landsat_NDVI', folder: EXPORT_FOLDER, fileFormat: 'CSV'});
Export.table.toDrive({collection: chirpsTable, description: 'AgroDigital_CHIRPS_Precip', folder: EXPORT_FOLDER, fileFormat: 'CSV'});
Export.table.toDrive({collection: era5TempTable, description: 'AgroDigital_ERA5_Temperature', folder: EXPORT_FOLDER, fileFormat: 'CSV'});
Export.table.toDrive({collection: era5RainTable, description: 'AgroDigital_ERA5_Precip', folder: EXPORT_FOLDER, fileFormat: 'CSV'});

// NASA POWER is exposed as an independent HTTP API; use the Colab script
// (or a separate authorized HTTP request) for POWER data.
