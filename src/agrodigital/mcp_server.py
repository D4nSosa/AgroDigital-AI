"""Model Context Protocol server for AgroDigital-AI."""
from __future__ import annotations


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP server requires the optional dependency. Install with: "
            "python -m pip install -e '.[ai]'"
        ) from exc

    from .agent_tools import (
        calculate_gdd, calculate_rainfall, get_capabilities, plan_analysis,
        process_sentinel2_scene, search_satellite_scenes,
    )
    from .raster import inspect_raster
    from .geo import validate_geojson

    server = FastMCP("AgroDigital-AI")

    @server.tool()
    def agro_plan_analysis(
        objective: str,
        aoi_geojson: dict | None = None,
        bbox: list[float] | None = None,
        date_range: str | None = None,
        crop_or_species: str | None = None,
        available_inputs: list[str] | None = None,
    ) -> dict:
        """Create an evidence-aware workflow plan from the user's request and supplied evidence."""
        return plan_analysis(
            objective, aoi_geojson=aoi_geojson, bbox=bbox, date_range=date_range,
            crop_or_species=crop_or_species, available_inputs=available_inputs,
        )

    @server.tool()
    def agro_capabilities() -> dict:
        """List the geospatial and scientific capabilities available in this runtime."""
        return get_capabilities()

    @server.tool()
    def agro_validate_geojson(geojson: dict) -> dict:
        """Validate GeoJSON structure and coordinate ranges; does not repair geometry."""
        return validate_geojson(geojson)

    @server.tool()
    def agro_search_satellite_scenes(
        datetime_range: str,
        bbox: list[float] | None = None,
        intersects: dict | None = None,
        collections: list[str] | None = None,
        cloud_cover_max: float | None = None,
        max_items: int = 10,
    ) -> dict:
        """Search public STAC metadata by EPSG:4326 bbox or GeoJSON geometry."""
        return search_satellite_scenes(
            bbox=bbox, intersects=intersects, datetime_range=datetime_range,
            collections=collections, cloud_cover_max=cloud_cover_max, max_items=max_items,
        )

    @server.tool()
    def agro_process_sentinel2_scene(
        item_id: str, output_dir: str,
        output_path: str | None = None,
        collection: str = "sentinel-2-l2a",
        max_bytes_per_asset: int = 2_000_000_000,
        use_scl: bool = True,
        overwrite: bool = False,
        aoi_geojson: dict | None = None,
    ) -> dict:
        """Download public Sentinel-2 assets, calculate NDVI and optionally clip to a GeoJSON AOI."""
        return process_sentinel2_scene(
            item_id, output_dir, output_path=output_path, collection=collection,
            max_bytes_per_asset=max_bytes_per_asset, use_scl=use_scl,
            overwrite=overwrite, aoi_geojson=aoi_geojson,
        )

    @server.tool()
    def agro_inspect_raster(path: str) -> dict:
        """Inspect a local raster file's dimensions, CRS, bands, transform and nodata."""
        return inspect_raster(path)

    @server.tool()
    def agro_calculate_gdd(tmin_c: float, tmax_c: float, base_c: float,
                           upper_c: float | None = None) -> dict:
        """Calculate daily growing degree days from supplied temperatures in Celsius."""
        return calculate_gdd(tmin_c, tmax_c, base_c, upper_c)

    @server.tool()
    def agro_calculate_rainfall(values_mm: list[float]) -> dict:
        """Sum supplied rainfall observations in millimetres; does not fetch weather data."""
        return calculate_rainfall(values_mm)

    server.run(transport="stdio")


if __name__ == "__main__":
    main()
