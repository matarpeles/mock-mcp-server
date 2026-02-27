import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    async with sse_client("http://localhost:8000/datadog/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test calling search_datadog_logs
            result = await session.call_tool(
                "search_datadog_logs",
                arguments={
                    "query": "checkout-service",
                    "port_context": {
                        "entities": {
                            "services": [
                                {"name": "checkout-service", "tier": "critical"},
                                {"name": "order-service", "tier": "high"},
                                {"name": "payment-service", "tier": "critical"}
                            ],
                            "incidents": [
                                {"title": "500 errors on checkout", "severity": "P1"}
                            ]
                        },
                        "hint": {
                            "direction": "found_issue",
                            "guidance": "Find error logs related to 500 errors"
                        }
                    }
                }
            )
            print(json.dumps(json.loads(result.content[0].text), indent=2))

asyncio.run(test())
