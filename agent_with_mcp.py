import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

def create_agent():
    """Create an agent with MCP integration"""
    # Get MCP server URL from environment
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    
    # Create tools list
    tools = []
    
    # Add MCP toolset if server URL is configured
    if mcp_server_url and mcp_server_url != "http://localhost:3000/mcp":
        print(f"🔧 Configuring MCP connection to: {mcp_server_url}")
        try:
            mcp_toolset = MCPToolset(
                connection_params=SseConnectionParams(
                    url=mcp_server_url
                )
            )
            tools.append(mcp_toolset)
            print("✅ MCP toolset configured successfully")
        except Exception as e:
            print(f"⚠️  MCP toolset configuration failed: {e}")
            print("   Continuing with basic agent (no MCP tools)")
    else:
        print("ℹ️  MCP_SERVER_URL not configured, starting without MCP tools")
        print("   Set MCP_SERVER_URL in .env file to enable MCP integration")
    
    # Create agent with MCP tools
    agent = LlmAgent(
        name="local_mcp_agent",
        model="gpt-4o",
        instruction="""
You are an AI assistant with access to local tools via MCP (Model Context Protocol).
When you have tools available, you can invoke them to help users with various tasks.
If no tools are available, provide helpful responses based on your training.

When invoking tools:
1. Use the appropriate tool for the task
2. Provide clear explanations of what you're doing
3. Handle errors gracefully
4. Give meaningful results to the user

Available capabilities depend on the MCP server configuration.
""",
        tools=tools,
    )
    
    return agent

# Create the agent
root_agent = create_agent()

# Keep agent variable for backward compatibility
agent = root_agent

def test_mcp_connection():
    """Test MCP server connection"""
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    
    if not mcp_server_url or mcp_server_url == "http://localhost:3000/mcp":
        print("⚠️  MCP server URL not configured")
        return False
    
    try:
        import requests
        response = requests.get(mcp_server_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ MCP server is accessible at {mcp_server_url}")
            return True
        else:
            print(f"❌ MCP server returned status code: {response.status_code}")
            return False
    except ImportError:
        print("⚠️  requests library not available for MCP testing")
        return False
    except Exception as e:
        print(f"❌ Could not connect to MCP server: {e}")
        return False

# Console interface for testing
if __name__ == "__main__":
    print("🚀 Starting ADK Agent with MCP Integration")
    print("=" * 50)
    
    # Test MCP connection
    mcp_available = test_mcp_connection()
    
    print("=" * 50)
    print("Type 'exit' to quit")
    print()
    
    try:
        from google.adk.runners import InMemoryRunner
        
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            print("❌ Please set your OPENAI_API_KEY in the .env file")
            print("Create a .env file with: OPENAI_API_KEY=your_actual_api_key")
            exit(1)
        
        # Create runner and start interactive session
        runner = InMemoryRunner()
        print("✅ Agent initialized successfully!")
        
        if mcp_available:
            print("🔧 MCP tools are available")
        else:
            print("⚠️  MCP tools are not available (basic mode)")
        
        print("You can now chat with the agent. Type 'exit' to quit.")
        print()
        
        # Simple interactive loop
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            try:
                # Run the agent with user input
                result = runner.chat(agent, user_input)
                print(f"Agent: {result.response}")
                print()
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
        
    except ImportError as e:
        print(f"❌ Error importing ADK runners: {e}")
        print("Please ensure google-adk is installed: pip install google-adk")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("Please check your OPENAI_API_KEY environment variable") 