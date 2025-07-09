import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime

print("🔍 OpenAI Connection Test")
print("=" * 50)

# Load environment variables
load_dotenv()

def test_environment():
    """Test OpenAI environment setup"""
    print("\n🌍 Environment Check:")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"   ✅ OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
    else:
        print("   ❌ OPENAI_API_KEY: Not set")
        return False
    
    return True

def test_direct_openai():
    """Test direct OpenAI API call"""
    print("\n🔗 Direct OpenAI API Test:")
    
    try:
        import openai
        
        # Create client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print("   🔧 Making direct API call...")
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello! Just say 'Hi' back."}],
            max_tokens=50,
            timeout=30
        )
        
        print(f"   ✅ Direct OpenAI call successful!")
        print(f"   📝 Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct OpenAI call failed: {e}")
        return False

def test_litellm():
    """Test LiteLLM (what ADK uses)"""
    print("\n🔗 LiteLLM Test:")
    
    try:
        from google.adk.models.lite_llm import LiteLlm
        
        print("   🔧 Creating LiteLLM model...")
        
        model = LiteLlm(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=100
        )
        
        print("   ✅ LiteLLM model created successfully!")
        print(f"   📝 Model type: {type(model)}")
        
        return model
        
    except Exception as e:
        print(f"   ❌ LiteLLM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_agent_simple_message():
    """Test agent with a simple message"""
    print("\n💬 Agent Message Test:")
    
    try:
        from billy_agent import root_agent
        
        print("   🔧 Testing simple message processing...")
        
        # Create a simple context for testing
        from google.adk.core.invocation_context import InvocationContext
        
        # This is tricky - we need to properly create an InvocationContext
        # Let's try a simpler approach by testing the agent's model directly
        
        print("   🔧 Testing agent's model directly...")
        
        # Get the model from the agent
        model = root_agent.model
        
        # Test the model directly
        messages = [{"role": "user", "content": "Hello! Just say 'Hi' back."}]
        
        print("   🔧 Making model call...")
        
        # This should work if the model is properly configured
        import asyncio
        
        # Try to call the model directly
        result = await asyncio.wait_for(
            model.generate_content_async(messages),
            timeout=30.0
        )
        
        print(f"   ✅ Model call successful!")
        print(f"   📝 Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent message test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adk_agent_structure():
    """Test ADK agent structure and methods"""
    print("\n🤖 ADK Agent Structure Test:")
    
    try:
        from billy_agent import root_agent
        
        print(f"   🔧 Agent type: {type(root_agent)}")
        print(f"   🔧 Agent name: {root_agent.name}")
        print(f"   🔧 Has model: {hasattr(root_agent, 'model')}")
        
        if hasattr(root_agent, 'model'):
            print(f"   🔧 Model type: {type(root_agent.model)}")
            print(f"   🔧 Model name: {root_agent.model.model}")
        
        print(f"   🔧 Has run_async: {hasattr(root_agent, 'run_async')}")
        
        if hasattr(root_agent, 'run_async'):
            import inspect
            sig = inspect.signature(root_agent.run_async)
            print(f"   🔧 run_async signature: {sig}")
            
            # Check if it's a coroutine function
            if inspect.iscoroutinefunction(root_agent.run_async):
                print("   ✅ run_async is a coroutine function")
            else:
                print("   ❌ run_async is NOT a coroutine function")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_tools():
    """Test MCP tools directly"""
    print("\n🛠️ MCP Tools Test:")
    
    try:
        from billy_agent import root_agent
        
        # Get tools from agent
        tools = root_agent.tools
        print(f"   🔧 Agent has {len(tools)} tools")
        
        for i, tool in enumerate(tools):
            print(f"   🔧 Tool {i+1}: {type(tool)}")
            
            # If it's an MCP toolset, test it
            if hasattr(tool, 'get_tools'):
                print(f"      - Has get_tools method")
                
                # Test getting tools
                try:
                    import asyncio
                    mcp_tools = asyncio.run(asyncio.wait_for(tool.get_tools(), timeout=10))
                    print(f"      - ✅ Found {len(mcp_tools)} MCP tools")
                    for mcp_tool in mcp_tools[:3]:  # Show first 3
                        print(f"         * {mcp_tool.name}")
                except Exception as e:
                    print(f"      - ❌ Error getting MCP tools: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print(f"🕐 Started at: {datetime.now()}")
    
    # Test 1: Environment
    if not test_environment():
        print("❌ Environment test failed - stopping")
        return
    
    # Test 2: Direct OpenAI
    openai_works = test_direct_openai()
    
    # Test 3: LiteLLM
    litellm_model = test_litellm()
    
    # Test 4: Agent structure
    agent_structure_works = test_adk_agent_structure()
    
    # Test 5: MCP tools
    mcp_tools_work = test_mcp_tools()
    
    # Test 6: Agent simple message (if other tests pass)
    if openai_works and litellm_model and agent_structure_works:
        await test_agent_simple_message()
    
    print(f"\n🕐 Completed at: {datetime.now()}")
    print("\n📋 Summary:")
    print(f"   OpenAI API: {'✅' if openai_works else '❌'}")
    print(f"   LiteLLM: {'✅' if litellm_model else '❌'}")
    print(f"   Agent Structure: {'✅' if agent_structure_works else '❌'}")
    print(f"   MCP Tools: {'✅' if mcp_tools_work else '❌'}")

if __name__ == "__main__":
    asyncio.run(main()) 