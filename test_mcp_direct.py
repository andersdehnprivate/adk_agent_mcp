#!/usr/bin/env python3
"""
Test MCP protocol over SSE connection
"""

import httpx
import asyncio
import json
from httpx_sse import aconnect_sse

async def test_mcp_protocol():
    """Test MCP protocol over SSE"""
    url = "http://localhost:3000/mcp/sse"
    
    print("Testing MCP protocol over SSE")
    print(f"URL: {url}")
    print("=" * 50)
    
    try:
        print("1. Testing basic SSE connection...")
        async with httpx.AsyncClient() as client:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            async with client.stream("GET", url, headers=headers, timeout=30) as response:
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    print(f"   ❌ Bad status code: {response.status_code}")
                    content = await response.aread()
                    print(f"   Response: {content.decode()}")
                    return
                
                print("   ✅ Connection established")
                print("   Reading SSE events...")
                
                # Read the first few chunks of data
                count = 0
                async for chunk in response.aiter_text():
                    print(f"   Chunk {count}: {chunk}")
                    count += 1
                    if count >= 3:  # Stop after 3 chunks
                        break
                        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. Testing MCP initialization message...")
    try:
        # Test sending an initialization message
        async with httpx.AsyncClient() as client:
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": False
                        }
                    },
                    "clientInfo": {
                        "name": "ADK Test Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Try POST to the endpoint
            response = await client.post(url, json=init_message, timeout=10)
            print(f"   POST Status: {response.status_code}")
            print(f"   POST Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ MCP initialization failed: {e}")
    
    print("\n" + "=" * 50)
    print("MCP protocol test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol()) 