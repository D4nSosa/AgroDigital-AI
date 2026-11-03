import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPServerIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_handshake_lists_and_calls_tools(self):
        params = StdioServerParameters(
            command="python",
            args=["-m", "agrodigital.mcp_server"],
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {tool.name for tool in tools.tools}

                expected = {
                    "agro_plan_analysis",
                    "agro_capabilities",
                    "agro_validate_geojson",
                    "agro_search_satellite_scenes",
                    "agro_process_sentinel2_scene",
                    "agro_inspect_raster",
                    "agro_calculate_gdd",
                    "agro_calculate_rainfall",
                }
                self.assertTrue(expected.issubset(names))

                capabilities = await session.call_tool("agro_capabilities", {})
                self.assertFalse(capabilities.isError)
                self.assertTrue(capabilities.content)

                plan = await session.call_tool(
                    "agro_plan_analysis",
                    {"objective": "Inspect a field image"},
                )
                self.assertFalse(plan.isError)
                self.assertTrue(plan.content)


if __name__ == "__main__":
    unittest.main()
