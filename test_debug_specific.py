import asyncio
import sys
import inspect
from datetime import datetime

print("🔍 Targeted Billy Agent Debug Test")
print("=" * 50)

# Add current directory to Python path
sys.path.insert(0, '.')

# Import the agent
from billy_agent import root_agent

def test_agent_methods():
    """Test agent methods in detail"""
    print("\n📋 Agent Method Analysis:")
    
    # Check run_async method
    if hasattr(root_agent, 'run_async'):
        print("   ✅ Has run_async method")
        
        # Get method signature
        sig = inspect.signature(root_agent.run_async)
        print(f"   📝 run_async signature: {sig}")
        
        # Check if it's a coroutine function
        if inspect.iscoroutinefunction(root_agent.run_async):
            print("   ✅ run_async is a coroutine function")
        else:
            print("   ❌ run_async is NOT a coroutine function")
    else:
        print("   ❌ No run_async method")
    
    # Check tools property
    if hasattr(root_agent, 'tools'):
        print("   ✅ Has tools property")
        print(f"   🛠️ Tools: {root_agent.tools}")
    else:
        print("   ❌ No tools property")
    
    # Check canonical_tools property
    if hasattr(root_agent, 'canonical_tools'):
        print("   ✅ Has canonical_tools property")
        try:
            tools = root_agent.canonical_tools
            print(f"   🛠️ Canonical tools count: {len(tools)}")
            for i, tool in enumerate(tools):
                print(f"      {i+1}. {tool.name}: {tool.description[:50]}...")
        except Exception as e:
            print(f"   ❌ Error accessing canonical_tools: {e}")
    else:
        print("   ❌ No canonical_tools property")

async def test_simple_run_async():
    """Test simple run_async call"""
    print("\n💬 Testing run_async with simple message:")
    
    try:
        print("   🔧 Creating message...")
        message = "Hello, can you help me?"
        
        print("   🔧 Calling run_async...")
        result = await root_agent.run_async(message)
        
        print(f"   ✅ Success! Result type: {type(result)}")
        print(f"   📝 Result: {str(result)[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_adk_agent_loader():
    """Test ADK agent loader properly"""
    print("\n🔍 Testing ADK Agent Loader:")
    
    try:
        from google.adk.cli.utils.agent_loader import AgentLoader
        import os
        
        # Get current directory
        current_dir = os.getcwd()
        print(f"   📁 Current directory: {current_dir}")
        
        # Create agent loader with current directory
        loader = AgentLoader(agents_dir=current_dir)
        print("   ✅ AgentLoader created successfully")
        
        # Try to load billy_agent
        print("   🔧 Loading billy_agent...")
        agent = loader.load_agent("billy_agent")
        
        print(f"   ✅ Agent loaded successfully!")
        print(f"   🤖 Agent type: {type(agent)}")
        print(f"   🤖 Agent id: {id(agent)}")
        
        # Compare with our root_agent
        print(f"   🔍 Same as root_agent? {agent is root_agent}")
        
        return agent
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_mcp_toolset_direct():
    """Test MCP toolset directly"""
    print("\n🔗 Testing MCP Toolset Directly:")
    
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        
        # Create toolset
        print("   🔧 Creating MCPToolset...")
        toolset = MCPToolset(
            connection_params=SseConnectionParams(url="http://localhost:3000/mcp/sse")
        )
        
        print("   ✅ MCPToolset created successfully")
        print(f"   🔧 Toolset type: {type(toolset)}")
        
        return toolset
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_mcp_toolset_get_tools(toolset):
    """Test getting tools from MCP toolset"""
    print("\n📋 Testing MCP Toolset get_tools:")
    
    if not toolset:
        print("   ❌ No toolset provided")
        return None
    
    try:
        print("   🔧 Getting tools...")
        tools = await asyncio.wait_for(toolset.get_tools(), timeout=15.0)
        
        print(f"   ✅ Success! Found {len(tools)} tools")
        for tool in tools:
            print(f"      - {tool.name}")
        
        return tools
        
    except asyncio.TimeoutError:
        print("   ❌ Timeout while getting tools")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main test function"""
    print(f"🕐 Started at: {datetime.now()}")
    
    # Test 1: Agent methods
    test_agent_methods()
    
    # Test 2: Simple run_async
    await test_simple_run_async()
    
    # Test 3: ADK agent loader
    adk_agent = test_adk_agent_loader()
    
    # Test 4: MCP toolset direct
    toolset = test_mcp_toolset_direct()
    
    # Test 5: MCP toolset get_tools
    if toolset:
        await test_mcp_toolset_get_tools(toolset)
    
    print(f"\n🕐 Completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main()) 