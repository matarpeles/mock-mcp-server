import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    async with sse_client("http://localhost:8000/datadog/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

asyncio.run(test())
