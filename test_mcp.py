#!/usr/bin/env python3

import os
import asyncio
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

async def test_mcp_connection():
    """Test MCP server connectivity"""
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    
    print(f"🔗 Testing MCP connection to: {mcp_server_url}")
    
    try:
        # Test MCP connection
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url=mcp_server_url
            )
        )
        
        print("✅ MCP toolset created successfully!")
        
        # Get tools (this is async)
        tools = await mcp_toolset.get_tools()
        print(f"📋 Found {len(tools)} MCP tools:")
        
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}: {tool.description}")
            
        return True
        
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_environment():
    """Test environment configuration"""
    print("🔧 Environment Configuration:")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    mcp_url = os.getenv("MCP_SERVER_URL")
    
    print(f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"  MCP_SERVER_URL: {mcp_url or '❌ Not set'}")
    
    return bool(openai_key and mcp_url)

async def main():
    print("🧪 MCP Connection Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    print()
    
    # Test MCP connection
    if env_ok:
        mcp_ok = await test_mcp_connection()
    else:
        print("❌ Environment not properly configured")
        mcp_ok = False
        
    print()
    print("📊 Summary:")
    print(f"  Environment: {'✅ OK' if env_ok else '❌ Failed'}")
    print(f"  MCP Connection: {'✅ OK' if mcp_ok else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(main()) 