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
        self._request_id = 1
    
    async def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        self._request_id += 1
        
        # Use a fresh session for each request to avoid event loop issues
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
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
        """Close the session - no longer needed with fresh sessions"""
        pass

# Global MCP client instance
_billy_mcp_client = None

async def get_billy_mcp_client():
    """Get or create the Billy.dk MCP client"""
    global _billy_mcp_client
    
    # Always create a fresh client to avoid session issues
    base_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    # Handle case where MCP_SERVER_URL already includes /mcp
    if base_url.endswith("/mcp"):
        mcp_url = base_url
    else:
        mcp_url = f"{base_url}/mcp"
    
    client = BillyDkMcpClient(mcp_url)
    await client.initialize()
    return client

# Billy.dk MCP Tool Functions
async def list_invoices() -> str:
    """List all invoices from Billy.dk. Use this when user asks about invoices, not customers."""
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
    """List all customers from Billy.dk. Use this when user asks about customers, not invoices."""
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

async def create_dynamic_mcp_tools():
    """
    Dynamically discover all available tools from the MCP server
    and create FunctionTool objects for each one.
    """
    try:
        # Get MCP client
        client = await get_billy_mcp_client()
        
        # Discover all available tools
        tools_result = await client.list_tools()
        
        if "tools" not in tools_result:
            print("⚠️  No tools found in MCP server response")
            return []
        
        discovered_tools = tools_result["tools"]
        print(f"🔍 Discovered {len(discovered_tools)} tools from MCP server")
        
        # Create dynamic FunctionTool objects for each discovered tool
        function_tools = []
        
        for tool_info in discovered_tools:
            tool_name = tool_info.get("name", "unknown")
            tool_description = tool_info.get("description", f"Tool: {tool_name}")
            tool_schema = tool_info.get("inputSchema", {})
            
            print(f"   📋 {tool_name}: {tool_description}")
            
            # Create dynamic function for this tool
            dynamic_func = create_dynamic_tool_function(tool_name, tool_description, tool_schema)
            
            # Create FunctionTool wrapper
            function_tools.append(FunctionTool(dynamic_func))
        
        return function_tools
        
    except Exception as e:
        print(f"❌ Error discovering MCP tools: {e}")
        print("   Falling back to hardcoded tools...")
        import traceback
        traceback.print_exc()
        
        # Fallback to hardcoded tools
        return [
            FunctionTool(list_invoices),
            FunctionTool(get_invoice),
            FunctionTool(create_invoice),
            FunctionTool(list_customers),
            FunctionTool(total_invoice_amount)
        ]

def create_dynamic_tool_function(tool_name: str, description: str, schema: Dict[str, Any]):
    """
    Create a dynamic function for an MCP tool.
    """
    
    # Extract parameter info from schema
    properties = schema.get("properties", {})
    required_params = schema.get("required", [])
    
    # Create function signature dynamically
    if not properties:
        # No parameters
        async def dynamic_tool() -> str:
            try:
                client = await get_billy_mcp_client()
                result = await client.call_tool(tool_name)
                
                if "content" in result and result["content"]:
                    return result["content"][0].get("text", str(result))
                return str(result)
            except Exception as e:
                return f"❌ Error calling {tool_name}: {e}"
        
        dynamic_tool.__name__ = tool_name
        dynamic_tool.__doc__ = description
        return dynamic_tool
    
    else:
        # Has parameters - create function with **kwargs
        async def dynamic_tool(**kwargs) -> str:
            try:
                client = await get_billy_mcp_client()
                result = await client.call_tool(tool_name, kwargs)
                
                if "content" in result and result["content"]:
                    return result["content"][0].get("text", str(result))
                return str(result)
            except Exception as e:
                return f"❌ Error calling {tool_name}: {e}"
        
        dynamic_tool.__name__ = tool_name
        dynamic_tool.__doc__ = description
        return dynamic_tool

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
    
    # Add Billy.dk MCP tools using standard HTTP protocol - DYNAMIC DISCOVERY
    if mcp_server_url:
        try:
            print(f"🔧 Billy.dk MCP integration using standard HTTP protocol")
            # Handle case where MCP_SERVER_URL already includes /mcp
            if mcp_server_url.endswith("/mcp"):
                server_display = mcp_server_url
            else:
                server_display = f"{mcp_server_url}/mcp"
            print(f"📡 Server: {server_display}")
            
            # Dynamically discover all available tools from MCP server
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task instead
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, create_dynamic_mcp_tools())
                    billy_tools = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                billy_tools = asyncio.run(create_dynamic_mcp_tools())
            
            tools.extend(billy_tools)
            
            print("✅ Billy.dk MCP tools added using standard protocol")
            print(f"📋 Discovered {len(billy_tools)} tools from MCP server")
            
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

CRITICAL: Always maintain conversation context and understand what data type you're working with.

When users ask about invoices, customers, or financial data, use the appropriate tools to provide accurate, up-to-date information.

You have access to Billy.dk business management tools that will be automatically available to you. Use the tools as needed based on user requests.

Context Awareness Rules:
1. If the user just showed/discussed CUSTOMERS, follow-up questions about "latest", "recent", "show me X" refer to CUSTOMERS
2. If the user just showed/discussed INVOICES, follow-up questions about "latest", "recent", "show me X" refer to INVOICES
3. If unclear, ask for clarification: "Do you mean customers or invoices?"
4. Pay attention to the current conversation topic - don't switch between customers and invoices randomly

Always:
- Be helpful and professional
- MAINTAIN CONVERSATION CONTEXT - remember what data type we're discussing
- Use tools when relevant to the user's request
- Explain what you're doing when using tools
- Format responses in a clear, readable way
- For dates, use YYYY-MM-DD format
- If asked for "latest X" or "recent X", understand this refers to the current topic of conversation

If a tool fails, inform the user politely and suggest alternatives.

Keep responses concise and focused, but always stay contextually aware.""",
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