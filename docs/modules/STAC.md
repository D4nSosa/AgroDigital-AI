# Public satellite catalog discovery

AgroDigital-AI includes a minimal STAC API client for public catalog discovery. The default endpoint is AWS Earth Search; another HTTPS STAC API can be selected explicitly.

Search by bbox or GeoJSON intersection, date interval, collection and optional cloud-cover threshold. Results include Item IDs, dates, cloud-cover metadata, geometry/bbox, asset URLs and available asset metadata.

The search remains discovery only. It does not itself download imagery. For a complete Sentinel-2 L2A scene workflow, select a returned Item ID and run:

~~~bash
agrodigital sentinel2-stac-ndvi --item-id "STAC_ITEM_ID" --output-dir ./results
~~~

The processing workflow retrieves the full STAC Item, downloads red/NIR and optionally SCL assets, derives reflectance scale/offset parameters from Item metadata, aligns categorical SCL to the red/NIR grid using nearest-neighbour resampling, and calculates NDVI. It records Item ID, collection, date, cloud cover, license URL, asset keys and parameters.

Catalog metadata, item availability and licensing can change. Verify the Item and license before operational use. A catalog hit is not proof that the scene is suitable for the intended analysis.
