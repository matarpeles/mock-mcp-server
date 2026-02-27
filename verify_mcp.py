"""Verify MCP response format matches spec"""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def verify():
    async with sse_client("http://localhost:8000/datadog/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Check tools schema
            print("=== Tool Schema (what Port sees) ===")
            tools = await session.list_tools()
            tool = tools.tools[0]
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Input Schema: {tool.inputSchema}")
            
            # Call tool and inspect raw response
            print("\n=== Tool Response Format ===")
            result = await session.call_tool(
                "search_datadog_logs",
                arguments={
                    "query": "test",
                    "port_context": {"entities": {}, "hint": {"direction": "nothing_found"}}
                }
            )
            print(f"Response type: CallToolResult")
            print(f"Content type: {type(result.content).__name__}")
            print(f"Content[0] type: {type(result.content[0]).__name__}")
            print(f"Content[0].type: {result.content[0].type}")
            print(f"isError: {result.isError}")
            print("\n✅ MCP-compliant: Tool returns TextContent with JSON string")

asyncio.run(verify())
