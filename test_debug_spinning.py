import asyncio
import sys
import traceback
from datetime import datetime
import json

print("🔍 ADK Billy Agent Debugging Test")
print("=" * 50)

def test_step(step_name, test_func):
    """Helper to run test steps with error handling"""
    try:
        print(f"\n⏳ {step_name}...")
        result = test_func()
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        print(f"✅ {step_name} - SUCCESS")
        return result
    except Exception as e:
        print(f"❌ {step_name} - FAILED: {e}")
        traceback.print_exc()
        return None

# Test 1: Import and Agent Creation
def test_import_and_creation():
    """Test basic import and agent creation"""
    sys.path.insert(0, '.')
    
    # Test importing the module
    from billy_agent import create_billy_agent, root_agent
    print(f"   📦 Module imported successfully")
    
    # Test root_agent exists
    print(f"   🤖 root_agent type: {type(root_agent)}")
    print(f"   🤖 root_agent id: {id(root_agent)}")
    
    # Test creating new agent
    new_agent = create_billy_agent()
    print(f"   🆕 New agent type: {type(new_agent)}")
    
    return root_agent

# Test 2: Agent Structure and Properties
def test_agent_structure(agent):
    """Test agent structure and properties"""
    print(f"   🔧 Agent class: {agent.__class__.__name__}")
    print(f"   🔧 Agent attributes: {dir(agent)}")
    
    # Check for essential methods
    essential_methods = ['run', 'run_async', 'get_tools']
    for method in essential_methods:
        if hasattr(agent, method):
            print(f"   ✅ Has {method} method")
        else:
            print(f"   ❌ Missing {method} method")
    
    # Try to get tools
    try:
        tools = agent.get_tools()
        print(f"   🛠️ Tools count: {len(tools)}")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description[:50]}...")
    except Exception as e:
        print(f"   ❌ Error getting tools: {e}")
    
    return agent

# Test 3: MCP Connection Test
async def test_mcp_connection():
    """Test MCP connection independently"""
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
    
    try:
        print("   🔗 Creating MCP toolset...")
        mcp_toolset = MCPToolset(
            connection_params=SseConnectionParams(url="http://localhost:3000/mcp/sse")
        )
        
        print("   📋 Getting tools with timeout...")
        tools = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=10.0)
        
        print(f"   ✅ MCP Connection successful! Found {len(tools)} tools")
        for tool in tools:
            print(f"      - {tool.name}")
            
        return mcp_toolset
    except Exception as e:
        print(f"   ❌ MCP Connection failed: {e}")
        return None

# Test 4: Tool Execution Test
async def test_tool_execution(mcp_toolset):
    """Test actual tool execution"""
    if not mcp_toolset:
        print("   ⚠️ No MCP toolset available")
        return
    
    try:
        tools = await mcp_toolset.get_tools()
        
        # Find listInvoices tool
        list_invoices_tool = None
        for tool in tools:
            if tool.name == "listInvoices":
                list_invoices_tool = tool
                break
        
        if not list_invoices_tool:
            print("   ❌ listInvoices tool not found")
            return
        
        print("   🔧 Executing listInvoices tool...")
        result = await asyncio.wait_for(
            list_invoices_tool.run({}), 
            timeout=15.0
        )
        
        print(f"   ✅ Tool execution successful!")
        print(f"   📄 Result type: {type(result)}")
        print(f"   📄 Result: {str(result)[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Tool execution failed: {e}")
        traceback.print_exc()
        return None

# Test 5: Agent Message Processing
async def test_agent_message_processing(agent):
    """Test agent message processing"""
    try:
        print("   💬 Testing simple message processing...")
        
        # Test with a simple message
        message = "Hello, how are you?"
        
        if hasattr(agent, 'run_async'):
            result = await asyncio.wait_for(
                agent.run_async(message), 
                timeout=30.0
            )
        elif hasattr(agent, 'run'):
            result = await asyncio.wait_for(
                asyncio.to_thread(agent.run, message), 
                timeout=30.0
            )
        else:
            print("   ❌ Agent has no run method")
            return None
        
        print(f"   ✅ Message processing successful!")
        print(f"   📝 Response type: {type(result)}")
        print(f"   📝 Response: {str(result)[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Message processing failed: {e}")
        traceback.print_exc()
        return None

# Test 6: ADK Integration Test
def test_adk_integration():
    """Test ADK integration"""
    try:
        # Test if agent can be loaded by ADK
        from google.adk.cli.utils.agent_loader import AgentLoader
        
        loader = AgentLoader()
        print("   🔍 Testing agent loading by ADK...")
        
        # Try to load the agent
        agent = loader.load_agent("billy_agent")
        print(f"   ✅ ADK agent loading successful!")
        print(f"   🤖 Loaded agent type: {type(agent)}")
        
        return agent
        
    except Exception as e:
        print(f"   ❌ ADK integration failed: {e}")
        traceback.print_exc()
        return None

# Test 7: Environment and Configuration
def test_environment():
    """Test environment configuration"""
    import os
    from dotenv import load_dotenv
    
    print("   🌍 Environment variables:")
    
    # Load .env file
    load_dotenv()
    
    # Check key environment variables
    env_vars = [
        "MCP_SERVER_URL",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * 10} (set)")
        else:
            print(f"   ❌ {var}: Not set")
    
    return True

# Main test execution
def main():
    """Run all debugging tests"""
    print(f"🕐 Test started at: {datetime.now()}")
    
    # Test 1: Import and creation
    agent = test_step("Import and Agent Creation", test_import_and_creation)
    
    # Test 2: Agent structure
    if agent:
        test_step("Agent Structure Analysis", lambda: test_agent_structure(agent))
    
    # Test 3: MCP connection
    mcp_toolset = test_step("MCP Connection Test", test_mcp_connection)
    
    # Test 4: Tool execution
    if mcp_toolset:
        test_step("Tool Execution Test", lambda: test_tool_execution(mcp_toolset))
    
    # Test 5: Agent message processing
    if agent:
        test_step("Agent Message Processing", lambda: test_agent_message_processing(agent))
    
    # Test 6: ADK integration
    test_step("ADK Integration Test", test_adk_integration)
    
    # Test 7: Environment
    test_step("Environment Configuration", test_environment)
    
    print(f"\n🕐 Test completed at: {datetime.now()}")
    print("=" * 50)
    print("📋 Summary: Check above for any ❌ FAILED tests")

if __name__ == "__main__":
    main() 