import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

def create_mcp_agent():
    """Create an agent with MCP integration using proper SSE protocol"""
    # Get MCP server URL from environment - use base URL for SSE protocol
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    
    # Create tools list
    tools = []
    
    # Add MCP toolset if server URL is configured
    if mcp_server_url:
        try:
            print(f"🔧 Attempting to connect to MCP server at: {mcp_server_url}")
            # Construct the correct SSE endpoint URL
            # Server endpoint is at /mcp/sse, so we need to append /mcp/sse to the base URL
            if mcp_server_url.endswith('/mcp'):
                sse_url = f"{mcp_server_url}/sse"
            else:
                sse_url = f"{mcp_server_url}/mcp/sse"
            print(f"🔧 Trying SSE endpoint: {sse_url}")
            
            mcp_toolset = MCPToolset(
                connection_params=SseConnectionParams(
                    url=sse_url  # Use the full SSE URL
                )
            )
            tools.append(mcp_toolset)
            print(f"✅ MCP toolset added for URL: {sse_url}")
            print("📡 MCP tools enabled - will connect when first used")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize MCP toolset: {e}")
            print("Agent will be created without MCP tools")
            print("🔍 This is likely a connection issue with the MCP server")
    
    # Create LLM model
    model = LiteLlm(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create agent with tools
    agent = LlmAgent(
        name="billy_invoice_agent",
        model=model,
        tools=tools,
        instruction="""
        You are a helpful AI assistant with access to Billy.dk invoice and customer management tools.
        You can help with:
        - Listing and retrieving invoices
        - Managing customers
        - Creating new invoices and customers
        - Calculating totals and generating reports
        
        Always provide clear, helpful responses and suggest relevant actions when appropriate.
        
        If MCP tools are not working, I can still help with general questions.
        """
    )
    
    return agent

# Create the agent instance
root_agent = create_mcp_agent()

if __name__ == "__main__":
    # Test the agent
    print("MCP Agent created successfully!")
    print(f"Agent name: {root_agent.name}")
    print(f"Available tools: {len(root_agent.tools)}")
    
    # Simple test
    try:
        response = root_agent.send_message("Hello! Can you help me with invoice management?")
        print(f"\nTest response: {response}")
    except Exception as e:
        print(f"Test failed: {e}") 