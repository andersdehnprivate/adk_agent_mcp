#!/usr/bin/env python3
"""
Simple test to check MCP server availability
"""

import httpx
import asyncio

async def test_mcp_simple():
    """Simple MCP server test"""
    print("Testing MCP server availability")
    print("=" * 40)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Health endpoint OK")
                data = response.json()
                print(f"   Server: {data.get('server', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False
    
    # Test 2: SSE endpoint connection
    print("\n2. Testing SSE endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            # Just test that we can connect (200 status)
            async with client.stream("GET", "http://localhost:3000/mcp/sse", headers=headers, timeout=3) as response:
                if response.status_code == 200:
                    print("   ✅ SSE endpoint accessible")
                    print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                    return True
                else:
                    print(f"   ❌ SSE endpoint failed: {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ SSE endpoint error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mcp_simple())
    if result:
        print("\n✅ MCP server is working correctly!")
    else:
        print("\n❌ MCP server has issues") 