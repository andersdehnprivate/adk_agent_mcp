import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

def create_billy_agent():
    """
    Create a clean Billy.dk MCP agent using the updated server specification.
    
    The new server (v1.0.0) now:
    - Returns human-readable responses (no formatting patches needed)
    - Handles session management properly (no race condition fixes needed)
    - Uses standard MCP protocol (no monkey patching needed)
    - Supports ADK-compatible SSE endpoints
    """
    
    # Get configuration
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Create tools list
    tools = []
    
    # Add Billy.dk MCP toolset
    if mcp_server_url:
        try:
            print(f"🔧 Connecting to Billy.dk MCP server at: {mcp_server_url}")
            
            # Use ADK-compatible SSE endpoint
            # Server specification: GET /mcp for SSE stream, POST /messages for tool calls
            sse_url = f"{mcp_server_url}/mcp/sse"
            
            mcp_toolset = MCPToolset(
                connection_params=SseConnectionParams(url=sse_url)
            )
            tools.append(mcp_toolset)
            
            print(f"✅ Billy.dk MCP toolset connected: {sse_url}")
            print("📋 Available tools: listInvoices, getInvoice, createInvoice, updateInvoice, deleteInvoice")
            print("👥 Customer tools: listCustomers, createCustomer")
            print("📦 Product tools: listProducts, createProduct")
            print("💰 Analytics: totalInvoiceAmount")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Billy.dk MCP server: {e}")
            print("💡 Make sure the server is running on http://localhost:3000")
            print("🔄 Agent will be created without MCP tools")
    
    # Create LLM model
    model = LiteLlm(
        model="gpt-4o-mini",
        api_key=openai_api_key
    )
    
    # Create agent with Billy.dk context
    agent = LlmAgent(
        name="billy_invoice_agent",
        model=model,
        tools=tools,
        instruction="""You are a helpful AI assistant for Billy.dk invoice and customer management.

You have access to these Billy.dk tools:
- **Invoice Management**: List, get, create, update, delete invoices
- **Customer Management**: List and create customers  
- **Product Management**: List and create products
- **Analytics**: Calculate total invoice amounts for date ranges

Key capabilities:
- List all invoices with details (amounts, dates, status)
- Get specific invoice information
- Create new invoices for customers
- Manage customer database
- Generate financial reports and totals
- Track invoice status (draft, sent, paid)

Always provide clear, helpful responses with relevant invoice details like amounts, dates, and statuses.
Use the tools to give accurate, up-to-date information from the Billy.dk system.

If you encounter any issues with the tools, explain what went wrong and suggest alternatives."""
    )
    
    return agent

def main():
    """Main function for testing the agent"""
    try:
        agent = create_billy_agent()
        print("🎉 Billy.dk agent created successfully!")
        return agent
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

if __name__ == "__main__":
    main() 