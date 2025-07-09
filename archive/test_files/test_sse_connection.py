#!/usr/bin/env python3
"""
Test SSE connection to MCP server
"""

import httpx
import asyncio
from httpx_sse import aconnect_sse

async def test_sse_connection():
    """Test SSE connection to MCP server"""
    url = "http://localhost:3000/mcp/sse"
    
    print("Testing SSE connection to MCP server")
    print(f"URL: {url}")
    print("=" * 50)
    
    try:
        print("1. Testing basic GET request...")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Content: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Basic GET failed: {e}")
    
    print("\n2. Testing SSE connection...")
    try:
        async with httpx.AsyncClient() as client:
            async with aconnect_sse(client, "GET", url) as event_source:
                print("   ✅ SSE connection established")
                print("   Waiting for events...")
                
                # Wait for first event with timeout
                count = 0
                async for event in event_source:
                    print(f"   Event {count}: {event}")
                    count += 1
                    if count >= 3:  # Stop after 3 events
                        break
                        
    except Exception as e:
        print(f"   ❌ SSE connection failed: {e}")
    
    print("\n3. Testing with MCP initialization...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        async with httpx.AsyncClient() as client:
            async with aconnect_sse(client, "GET", url, headers=headers) as event_source:
                print("   ✅ MCP SSE connection established")
                print("   Waiting for MCP events...")
                
                count = 0
                async for event in event_source:
                    print(f"   MCP Event {count}: {event}")
                    count += 1
                    if count >= 3:  # Stop after 3 events
                        break
                        
    except Exception as e:
        print(f"   ❌ MCP SSE connection failed: {e}")
    
    print("\n" + "=" * 50)
    print("SSE connection test completed!")

if __name__ == "__main__":
    asyncio.run(test_sse_connection()) 