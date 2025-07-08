#!/usr/bin/env python3

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_basic_http():
    """Test basic HTTP connectivity to MCP server"""
    import aiohttp
    
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    print(f"🌐 Testing basic HTTP connectivity to: {mcp_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(mcp_url) as response:
                print(f"✅ HTTP Response: {response.status}")
                text = await response.text()
                print(f"📄 Response body: {text[:200]}...")
                return True
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        return False

async def test_mcp_toolset():
    """Test MCP toolset with detailed error handling"""
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
    
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    print(f"🔗 Testing MCP toolset connection to: {mcp_url}")
    
    try:
        # Create toolset
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url=mcp_url
            )
        )
        print("✅ MCP toolset created successfully!")
        
        # Try to get tools with timeout
        print("🛠️  Attempting to get tools...")
        try:
            tools = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=10.0)
            print(f"✅ Found {len(tools)} MCP tools:")
            
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.name}: {tool.description[:100]}...")
            
            return True
            
        except asyncio.TimeoutError:
            print("❌ Timeout while getting tools (10s)")
            return False
        except Exception as e:
            print(f"❌ Error getting tools: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Try to get more details about the error
            if hasattr(e, 'exceptions'):
                print(f"   Sub-exceptions: {e.exceptions}")
            
            return False
            
    except Exception as e:
        print(f"❌ Failed to create MCP toolset: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def test_mcp_server_type():
    """Try to determine what type of MCP server is running"""
    import aiohttp
    
    print("🔍 Investigating MCP server type...")
    
    # Test different common MCP endpoints
    test_urls = [
        "http://localhost:3000",
        "http://localhost:3000/health",
        "http://localhost:3000/mcp",
        "http://localhost:3000/mcp/health",
        "http://localhost:3000/api",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            try:
                async with session.get(url, timeout=3) as response:
                    print(f"  {url}: {response.status}")
                    
                    # Check content type
                    content_type = response.headers.get('content-type', 'unknown')
                    print(f"    Content-Type: {content_type}")
                    
                    # Show first bit of response
                    if response.status < 500:
                        text = await response.text()
                        if text:
                            print(f"    Response: {text[:100]}...")
                        
            except Exception as e:
                print(f"  {url}: ❌ {e}")

async def main():
    """Main diagnostic function"""
    print("🧪 Detailed MCP Connection Diagnostics")
    print("=" * 60)
    
    # Check environment
    openai_key = os.getenv("OPENAI_API_KEY")
    mcp_url = os.getenv("MCP_SERVER_URL")
    
    print("🔧 Environment:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"  MCP_SERVER_URL: {mcp_url or '❌ Not set'}")
    print()
    
    # Test basic HTTP connectivity
    http_ok = await test_basic_http()
    print()
    
    # Investigate server type
    await test_mcp_server_type()
    print()
    
    # Test MCP toolset
    mcp_ok = await test_mcp_toolset()
    print()
    
    # Summary
    print("📊 Summary:")
    print(f"  Environment: {'✅ OK' if openai_key and mcp_url else '❌ Failed'}")
    print(f"  HTTP Connectivity: {'✅ OK' if http_ok else '❌ Failed'}")
    print(f"  MCP Toolset: {'✅ OK' if mcp_ok else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(main()) 