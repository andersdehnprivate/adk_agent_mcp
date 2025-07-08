import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

def create_mcp_agent():
    """Create an agent with MCP integration"""
    # Get MCP server URL from environment
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    
    # Create tools list
    tools = []
    
    # Add MCP toolset if server URL is configured
    if mcp_server_url:
        try:
            mcp_toolset = MCPToolset(
                connection_params=SseConnectionParams(
                    url=mcp_server_url
                )
            )
            tools.append(mcp_toolset)
            print(f"✅ MCP toolset added for URL: {mcp_server_url}")
        except Exception as e:
            print(f"❌ Failed to add MCP toolset: {e}")
            # Continue without MCP tools if configuration fails
            pass

    # Create agent with MCP tools
    agent = LlmAgent(
        name="mcp_agent",
        model=LiteLlm(model="openai/gpt-4o"),
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

# Create the agent for web interface
root_agent = create_mcp_agent() 