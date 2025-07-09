#!/usr/bin/env python3
"""
Simple test to verify MCP integration is working
"""

import asyncio
import requests
from agents.billy_agent.agent import create_mcp_agent

def test_server_health():
    """Test server health"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server health: OK")
            return True
        else:
            print(f"❌ Server health: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server health: ERROR - {e}")
        return False

def test_server_initialization():
    """Test server initialization endpoint"""
    try:
        init_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        response = requests.post("http://localhost:3000/mcp", json=init_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Server should acknowledge the message was sent via SSE
            if ("result" in data and 
                ("status" in data["result"] and
                 data["result"]["status"] in ["message_sent_via_sse", "sent"])):
                print("✅ Server initialization: OK")
                return True
            else:
                print(f"❌ Server initialization: Invalid response - {data}")
                return False
        else:
            print(f"❌ Server initialization: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server initialization: ERROR - {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    try:
        agent = create_mcp_agent()
        print("✅ Agent creation: OK")
        print(f"   Agent name: {agent.name}")
        print(f"   Tools count: {len(agent.tools)}")
        return True
    except Exception as e:
        print(f"❌ Agent creation: ERROR - {e}")
        return False

async def test_mcp_tools():
    """Test MCP tools functionality"""
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:3000/mcp/sse"
            )
        )
        
        # Try to get tools (this will test the actual MCP connection)
        tools = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=15.0)
        print(f"✅ MCP tools: Found {len(tools)} tools")
        for tool in tools[:3]:  # Show first 3 tools
            print(f"   - {tool.name}: {tool.description}")
        return True
    except asyncio.TimeoutError:
        print("❌ MCP tools: Timeout getting tools")
        return False
    except Exception as e:
        print(f"❌ MCP tools: ERROR - {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MCP Integration Final Test")
    print("=" * 50)
    
    results = []
    
    print("\n1. Testing server health...")
    results.append(test_server_health())
    
    print("\n2. Testing server initialization...")
    results.append(test_server_initialization())
    
    print("\n3. Testing agent creation...")
    results.append(test_agent_creation())
    
    print("\n4. Testing MCP tools...")
    results.append(asyncio.run(test_mcp_tools()))
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ MCP Integration is working correctly!")
        print("   - Server is responding properly")
        print("   - Agent creation is successful")
        print("   - MCP tools are accessible")
        print("   - Ready to use in ADK web interface")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("\n❌ Issues remain in MCP integration")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 