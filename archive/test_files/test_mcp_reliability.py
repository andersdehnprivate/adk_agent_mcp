#!/usr/bin/env python3
"""
Test MCP server reliability
"""

import httpx
import asyncio
import time

async def test_mcp_server_reliability():
    """Test if MCP server is consistently available"""
    url = "http://localhost:3000/mcp/sse"
    
    print("Testing MCP server reliability")
    print(f"URL: {url}")
    print("=" * 50)
    
    # Test multiple connections in quick succession
    success_count = 0
    total_tests = 10
    
    for i in range(total_tests):
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
                
                # Test with streaming connection for SSE
                async with client.stream("GET", url, headers=headers, timeout=5) as response:
                    if response.status_code == 200:
                        success_count += 1
                        print(f"Test {i+1}: ✅ Success (200)")
                        
                        # Try to read first chunk to verify it's working
                        async for chunk in response.aiter_text():
                            if chunk:
                                print(f"         First chunk: {chunk[:100]}...")
                                break
                    else:
                        print(f"Test {i+1}: ❌ Failed ({response.status_code})")
                        content = await response.aread()
                        print(f"         Response: {content.decode()[:200]}...")
                    
        except Exception as e:
            print(f"Test {i+1}: ❌ Error: {type(e).__name__}: {e}")
            import traceback
            print(f"         Details: {traceback.format_exc().split('\\n')[-3]}")
        
        # Small delay between tests
        await asyncio.sleep(0.1)
    
    print(f"\nResults: {success_count}/{total_tests} successful")
    
    if success_count == total_tests:
        print("✅ MCP server is consistently available!")
        return True
    else:
        print("❌ MCP server has reliability issues")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_server_reliability()) 