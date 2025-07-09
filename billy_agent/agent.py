import os
import json
import asyncio
import aiohttp
from typing import Any, Dict, List
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool

# Load environment variables
load_dotenv()

class BillyDkMcpClient:
    """
    Custom Billy.dk MCP client using standard HTTP/JSON-RPC protocol.
    This follows the official MCP specification, not the custom SSE protocol.
    """
    
    def __init__(self, mcp_url: str = "http://localhost:3000/mcp"):
        self.mcp_url = mcp_url
        self.session = None
        self._request_id = 1
    
    async def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        self._request_id += 1
        
        try:
            async with self.session.post(
                self.mcp_url,
                headers={"Content-Type": "application/json"},
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", {})
        
        except Exception as e:
            print(f"❌ Billy.dk MCP request failed: {e}")
            raise
    
    async def initialize(self):
        """Initialize the MCP session"""
        try:
            result = await self._make_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "adk-billy-client",
                    "version": "1.0.0"
                }
            })
            print("✅ Billy.dk MCP session initialized")
            return result
        except Exception as e:
            print(f"⚠️  Billy.dk MCP initialization failed: {e}")
            raise
    
    async def list_tools(self):
        """List available tools"""
        return await self._make_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None):
        """Call a specific tool"""
        return await self._make_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

# Global MCP client instance
_billy_mcp_client = None

async def get_billy_mcp_client():
    """Get or create the Billy.dk MCP client"""
    global _billy_mcp_client
    if not _billy_mcp_client:
        base_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
        # Handle case where MCP_SERVER_URL already includes /mcp
        if base_url.endswith("/mcp"):
            mcp_url = base_url
        else:
            mcp_url = f"{base_url}/mcp"
        _billy_mcp_client = BillyDkMcpClient(mcp_url)
        await _billy_mcp_client.initialize()
    return _billy_mcp_client

# Billy.dk MCP Tool Functions
async def list_invoices() -> str:
    """List all invoices from Billy.dk"""
    try:
        client = await get_billy_mcp_client()
        result = await client.call_tool("listInvoices")
        
        # Extract human-readable text from MCP response
        if "content" in result and result["content"]:
            return result["content"][0].get("text", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Error listing invoices: {e}"

async def get_invoice(invoice_id: str) -> str:
    """Get a specific invoice by ID"""
    try:
        client = await get_billy_mcp_client()
        result = await client.call_tool("getInvoice", {"id": invoice_id})
        
        if "content" in result and result["content"]:
            return result["content"][0].get("text", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Error getting invoice {invoice_id}: {e}"

async def create_invoice(contact_id: str, amount: float, state: str = "draft") -> str:
    """Create a new invoice"""
    try:
        client = await get_billy_mcp_client()
        result = await client.call_tool("createInvoice", {
            "contactId": contact_id,
            "amount": amount,
            "state": state
        })
        
        if "content" in result and result["content"]:
            return result["content"][0].get("text", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Error creating invoice: {e}"

async def list_customers() -> str:
    """List all customers from Billy.dk"""
    try:
        client = await get_billy_mcp_client()
        result = await client.call_tool("listCustomers")
        
        if "content" in result and result["content"]:
            return result["content"][0].get("text", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Error listing customers: {e}"

async def total_invoice_amount(start_date: str, end_date: str) -> str:
    """Get total invoice amount for a date range (YYYY-MM-DD format)"""
    try:
        client = await get_billy_mcp_client()
        result = await client.call_tool("totalInvoiceAmount", {
            "startDate": start_date,
            "endDate": end_date
        })
        
        if "content" in result and result["content"]:
            return result["content"][0].get("text", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Error getting total amount: {e}"

def create_billy_agent():
    """
    Create a Billy.dk agent with proper MCP integration using standard HTTP protocol.
    This follows the official MCP specification.
    """
    
    # Get configuration
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    
    # Check API key
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Please set OPENAI_API_KEY in your .env file")
    
    # Prepare tools list
    tools = []
    
    # Add Billy.dk MCP tools using standard HTTP protocol
    if mcp_server_url:
        try:
            print(f"🔧 Billy.dk MCP integration using standard HTTP protocol")
            # Handle case where MCP_SERVER_URL already includes /mcp
            if mcp_server_url.endswith("/mcp"):
                server_display = mcp_server_url
            else:
                server_display = f"{mcp_server_url}/mcp"
            print(f"📡 Server: {server_display}")
            
            # Create function tools for Billy.dk operations
            billy_tools = [
                FunctionTool(list_invoices),
                FunctionTool(get_invoice),
                FunctionTool(create_invoice),
                FunctionTool(list_customers),
                FunctionTool(total_invoice_amount)
            ]
            
            tools.extend(billy_tools)
            
            print("✅ Billy.dk MCP tools added using standard protocol")
            print("📋 Available tools: listInvoices, getInvoice, createInvoice, listCustomers, totalInvoiceAmount")
            
        except Exception as e:
            print(f"⚠️  Billy.dk MCP tool setup failed: {e}")
            print("   Agent will continue without MCP tools")
    else:
        print("⚠️  MCP_SERVER_URL not configured")
        print("   Set MCP_SERVER_URL=http://localhost:3000 in your .env file")
    
    # Create LiteLLM model for OpenAI support
    model = LiteLlm(
        model="openai/gpt-4o-mini",  # LiteLLM requires provider prefix format
        api_key=openai_api_key
    )
    
    # Create the agent using the official ADK pattern
    agent = LlmAgent(
        model=model,  # Use LiteLlm object for OpenAI model support
        name="billy_agent",   # Required: Unique agent name
        description="A helpful AI assistant specialized in managing business invoices, customers, and products using Billy.dk tools via standard MCP protocol.",  # Required: Agent description
        instruction="""You are Billy, a helpful AI assistant specialized in managing business invoices, customers, and products.

You have access to Billy.dk business management tools via the standard MCP protocol that allow you to:
- 📋 List, view, and create invoices
- 👥 Manage customer information  
- 💰 Analyze financial data and totals

When users ask about invoices, customers, or financial data, use the appropriate tools to provide accurate, up-to-date information.

Available tools:
- list_invoices(): Get all invoices
- get_invoice(invoice_id): Get specific invoice details
- create_invoice(contact_id, amount, state): Create new invoice
- list_customers(): Get all customers
- total_invoice_amount(start_date, end_date): Get total for date range

Always:
- Be helpful and professional
- Use tools when relevant to the user's request
- Explain what you're doing when using tools
- Format responses in a clear, readable way
- For dates, use YYYY-MM-DD format

If a tool fails, inform the user politely and suggest alternatives.

Keep responses concise and focused.""",
        tools=tools  # Billy.dk tools using standard MCP protocol
    )
    
    return agent

def main():
    """Main function for console testing"""
    print("🚀 Billy.dk ADK Agent - Console Mode")
    print("=" * 50)
    
    try:
        agent = create_billy_agent()
        print("✅ Agent created successfully!")
        print("💬 You can now interact with Billy...")
        print("   Type 'exit' to quit")
        print()
        
        # Simple console chat loop
        while True:
            user_input = input("User: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input:
                print("Agent: I'm ready to help with Billy.dk tools!")
                
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

# ADK expects a root_agent variable - following official documentation pattern
try:
    print("🎯 Creating root_agent for ADK web interface...")
    root_agent = create_billy_agent()
    print("✅ root_agent created successfully for ADK web interface")
    
except Exception as e:
    print(f"⚠️  Error creating root_agent: {e}")
    print("   Creating fallback agent...")
    import traceback
    traceback.print_exc()
    
    # Create a simple fallback agent with LiteLLM for OpenAI support
    try:
        # Create LiteLLM model for fallback
        fallback_model = LiteLlm(
            model="openai/gpt-3.5-turbo",  # LiteLLM requires provider prefix format
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        root_agent = LlmAgent(
            model=fallback_model,  # Use LiteLlm object for OpenAI model support
            name="billy_agent_fallback",  # Required: Unique name
            description="A helpful AI assistant. Billy.dk tools are currently unavailable.",  # Required: Description
            instruction="I'm Billy, a helpful AI assistant. Note: Billy.dk business management tools are currently unavailable due to setup issues. I can still help with general questions and assistance.",
            tools=[]  # No tools
        )
        print("🔄 Fallback agent created successfully")
        
    except Exception as fallback_error:
        print(f"❌ Fallback agent creation also failed: {fallback_error}")
        print("   ADK web interface will not work")
        root_agent = None 