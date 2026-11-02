# Weather and agrometeorology

Record provider/station, coordinates/elevation, timezone, observation versus forecast, units, aggregation period, missing values and update time. Do not merge station and gridded data without identifying their different spatial support.

Daily mean-method growing degree days: max(0, (Tmin + Tmax)/2 - Tbase). The library supports an optional upper cap. Crop-specific methods may require different thresholds and temperature-response curves.

Rainfall accumulation sums valid daily depths in millimetres. Missing values must be handled explicitly.

The current weather module calculates GDD and rainfall totals; it does not retrieve observations or forecasts.
