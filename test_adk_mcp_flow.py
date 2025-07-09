#!/usr/bin/env python3
"""
Test that mimics the exact ADK MCP connection flow
"""

import asyncio
import sys
import os

# Add the project root to the path so we can import google.adk modules
sys.path.insert(0, os.path.abspath('.'))

async def test_adk_mcp_flow():
    """Test the exact ADK MCP flow"""
    print("🧪 Testing ADK MCP Flow")
    print("=" * 50)
    
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        
        print("📡 Step 1: Creating MCPToolset...")
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:3000/mcp/sse"
            )
        )
        print("✅ MCPToolset created")
        
        print("\n📡 Step 2: Getting tools with 30s timeout...")
        try:
            tools = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=30.0)
            print(f"✅ Tools retrieved: {len(tools)} tools found")
            
            print("\n📋 Available tools:")
            for i, tool in enumerate(tools):
                print(f"   {i+1}. {tool.name}: {tool.description}")
            
            return True
            
        except asyncio.TimeoutError:
            print("❌ Timeout getting tools (30s)")
            return False
            
        except Exception as e:
            print(f"❌ Error getting tools: {e}")
            print(f"   Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure ADK is properly installed")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_adk_mcp_connection_details():
    """Test connection details step by step"""
    print("\n🔍 Testing connection details...")
    
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:3000/mcp/sse"
            )
        )
        
        # Try to access internal connection details
        print("📡 Checking internal connection state...")
        
        # This might give us more info about what's happening
        print(f"   URL: {mcp_toolset.connection_params.url}")
        
        # Try to get the first tool (this might be less intensive)
        print("\n📡 Testing get_tools() with detailed timing...")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            tools = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=20.0)
            end_time = asyncio.get_event_loop().time()
            
            print(f"✅ Success! Took {end_time - start_time:.2f} seconds")
            return True
            
        except asyncio.TimeoutError:
            end_time = asyncio.get_event_loop().time()
            print(f"❌ Timeout after {end_time - start_time:.2f} seconds")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

async def main():
    """Run all ADK MCP flow tests"""
    results = []
    
    results.append(await test_adk_mcp_flow())
    results.append(await test_adk_mcp_connection_details())
    
    print("\n" + "=" * 50)
    print("📊 ADK MCP FLOW RESULTS:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL ADK TESTS PASSED ({passed}/{total})")
        print("✅ ADK MCP integration is working!")
    else:
        print(f"⚠️  ADK TESTS FAILED ({passed}/{total})")
        print("❌ ADK MCP integration has issues")
        
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 