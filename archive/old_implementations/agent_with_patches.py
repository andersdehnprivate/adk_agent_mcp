import os
import json
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Load environment variables
load_dotenv()

# MONKEY PATCH: Fix SSE message handling for Billy.dk server compatibility
def patch_sse_client():
    """Monkey patch to handle raw data lines from Billy.dk server"""
    try:
        from mcp.client.sse import sse_client
        import asyncio
        import json
        
        # Store original function
        original_sse_client = sse_client
        
        async def patched_sse_client(url, headers=None, **kwargs):
            """Custom SSE client that handles both standard and raw data formats"""
            print(f"🔧 Using patched SSE client for: {url}")
            
            # Use original client but process messages differently
            async with original_sse_client(url, headers, **kwargs) as client:
                async for message in client:
                    # Handle standard MCP format
                    if hasattr(message, 'event') and hasattr(message, 'data'):
                        # Check if this is a tools/call response with raw JSON
                        if hasattr(message, 'data') and message.data:
                            try:
                                parsed = json.loads(message.data)
                                if ('result' in parsed and 'content' in parsed['result'] and 
                                    isinstance(parsed['result']['content'], list) and 
                                    len(parsed['result']['content']) > 0):
                                    
                                    content_item = parsed['result']['content'][0]
                                    if 'text' in content_item:
                                        text = content_item['text']
                                        try:
                                            # Try to parse as JSON - if it works, it's raw data
                                            json_data = json.loads(text)
                                            # Format the JSON data for human reading
                                            formatted_text = format_billy_response(json_data)
                                            # Replace the raw JSON with formatted text
                                            content_item['text'] = formatted_text
                                            message.data = json.dumps(parsed)
                                            print("✅ Formatted Billy.dk response for ADK")
                                        except:
                                            # Not JSON, leave as is
                                            pass
                            except:
                                # Not JSON, leave as is
                                pass
                        
                        yield message
                    # Handle raw JSON lines (Billy.dk compatibility)
                    elif hasattr(message, 'data') and message.data:
                        try:
                            # Try to parse as JSON
                            json.loads(message.data)
                            # Create proper SSE message structure
                            from collections import namedtuple
                            SSEMessage = namedtuple('SSEMessage', ['event', 'data'])
                            yield SSEMessage(event='message', data=message.data)
                        except (json.JSONDecodeError, AttributeError):
                            # Pass through original message
                            yield message
                    else:
                        # Pass through any other message types
                        yield message
        
        # Replace the original function
        import mcp.client.sse
        mcp.client.sse.sse_client = patched_sse_client
        print("✅ SSE client patched for Billy.dk compatibility with response formatting")
        
    except ImportError as e:
        print(f"⚠️ Could not patch SSE client: {e}")
        print("MCP tools may not work correctly with Billy.dk server format")

def format_billy_response(data):
    """Format Billy.dk JSON response into human-readable text"""
    try:
        if isinstance(data, list):
            # This is a list of invoices
            if len(data) == 0:
                return "No invoices found."
            
            # Format invoice list
            formatted = f"📋 Found {len(data)} invoices:\n\n"
            
            for i, invoice in enumerate(data[:10], 1):  # Show first 10 invoices
                invoice_no = invoice.get('invoiceNo', 'Draft')
                amount = invoice.get('grossAmount', 0)
                currency = invoice.get('currencyId', 'DKK')
                date = invoice.get('entryDate', 'N/A')
                state = invoice.get('state', 'unknown')
                contact_id = invoice.get('contactId', 'N/A')
                description = invoice.get('lineDescription', 'No description')
                
                formatted += f"{i}. Invoice #{invoice_no}\n"
                formatted += f"   💰 Amount: {amount} {currency}\n"
                formatted += f"   📅 Date: {date}\n"
                formatted += f"   📊 Status: {state}\n"
                formatted += f"   👤 Customer: {contact_id}\n"
                formatted += f"   📝 Description: {description}\n\n"
            
            if len(data) > 10:
                formatted += f"... and {len(data) - 10} more invoices.\n"
            
            return formatted
            
        elif isinstance(data, dict):
            # Single invoice or other object
            if 'invoiceNo' in data:
                # Single invoice
                invoice_no = data.get('invoiceNo', 'Draft')
                amount = data.get('grossAmount', 0)
                currency = data.get('currencyId', 'DKK')
                date = data.get('entryDate', 'N/A')
                state = data.get('state', 'unknown')
                description = data.get('lineDescription', 'No description')
                
                return f"📋 Invoice #{invoice_no}\n💰 Amount: {amount} {currency}\n📅 Date: {date}\n📊 Status: {state}\n📝 Description: {description}"
            else:
                # Other data structure
                return f"📋 Billy.dk Data:\n{json.dumps(data, indent=2)}"
        else:
            return str(data)
            
    except Exception as e:
        return f"📋 Billy.dk response received (formatting error: {e})\n\nRaw data: {str(data)[:500]}..."

def create_mcp_agent():
    """Create an agent with MCP integration using proper SSE protocol"""
    
    # Apply SSE compatibility patch
    patch_sse_client()
    
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
            print("📡 MCP tools enabled with Billy.dk compatibility patch and response formatting")
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
