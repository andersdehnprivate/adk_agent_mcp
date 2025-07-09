import asyncio
import httpx
import json
import uuid
from datetime import datetime

async def test_mcp_server_direct():
    """Test MCP server responses directly"""
    print("🔍 Testing MCP Server Direct Responses")
    print("=" * 50)
    
    session_id = str(uuid.uuid4())
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Initialize MCP connection
            print("1. Testing MCP initialization...")
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await client.post(
                "http://localhost:3000/mcp/request",
                json=init_payload,
                headers={"MCP-Session-Id": session_id}
            )
            
            if response.status_code == 200:
                print("   ✅ MCP initialization successful")
                init_result = response.json()
                print(f"   Server capabilities: {init_result.get('result', {}).get('capabilities', {})}")
            else:
                print(f"   ❌ MCP initialization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
            
            # Test 2: List available tools
            print("\n2. Testing tools list...")
            tools_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                "http://localhost:3000/mcp/request",
                json=tools_payload,
                headers={"MCP-Session-Id": session_id}
            )
            
            if response.status_code == 200:
                tools_result = response.json()
                tools = tools_result.get("result", {}).get("tools", [])
                print(f"   ✅ Found {len(tools)} tools")
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            else:
                print(f"   ❌ Tools list failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
            
            # Test 3: Call invoice tool to check response format
            print("\n3. Testing invoice tool response format...")
            invoice_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_invoices",
                    "arguments": {"limit": 3}
                }
            }
            
            response = await client.post(
                "http://localhost:3000/mcp/request",
                json=invoice_payload,
                headers={"MCP-Session-Id": session_id}
            )
            
            if response.status_code == 200:
                invoice_result = response.json()
                print(f"   ✅ Invoice tool call successful")
                
                # Check the response format
                result = invoice_result.get("result", {})
                content = result.get("content", [])
                
                print(f"   Response structure: {json.dumps(result, indent=2)}")
                
                if content:
                    first_content = content[0]
                    content_type = first_content.get("type", "unknown")
                    content_text = first_content.get("text", "")
                    
                    print(f"\n   Content type: {content_type}")
                    print(f"   Content preview: {content_text[:200]}...")
                    
                    # Check if it's still raw JSON
                    try:
                        parsed = json.loads(content_text)
                        print("   ⚠️  WARNING: Response is still raw JSON!")
                        print(f"   First item: {parsed[0] if parsed else 'No items'}")
                        return "RAW_JSON"
                    except json.JSONDecodeError:
                        print("   ✅ Response is human-readable text (not raw JSON)")
                        return "HUMAN_READABLE"
                else:
                    print("   ❌ No content in response")
                    return "NO_CONTENT"
            else:
                print(f"   ❌ Invoice tool call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return "FAILED"
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return "EXCEPTION"

async def test_adk_mcp_integration():
    """Test full ADK MCP integration flow"""
    print("\n🔍 Testing Full ADK MCP Integration")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test ADK's MCP tool endpoint
            print("1. Testing ADK MCP tool integration...")
            
            # This simulates what ADK does internally
            adk_payload = {
                "tool_name": "get_invoices",
                "tool_args": {"limit": 3}
            }
            
            # Note: This is a hypothetical endpoint - we need to find the actual ADK MCP endpoint
            response = await client.post(
                "http://localhost:8000/tools/mcp/billy",
                json=adk_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ ADK MCP integration successful")
                print(f"   Result: {json.dumps(result, indent=2)}")
                return "SUCCESS"
            else:
                print(f"   ❌ ADK MCP integration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return "FAILED"
                
    except Exception as e:
        print(f"❌ ADK integration test failed: {e}")
        return "EXCEPTION"

async def main():
    """Run all tests to diagnose the spinning issue"""
    print("🚀 Comprehensive MCP Flow Testing")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Direct MCP server
    server_result = await test_mcp_server_direct()
    
    # Test 2: Full ADK integration
    adk_result = await test_adk_mcp_integration()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"MCP Server Response Format: {server_result}")
    print(f"ADK Integration Status: {adk_result}")
    
    if server_result == "RAW_JSON":
        print("\n❌ ISSUE IDENTIFIED: MCP server still returns raw JSON!")
        print("   The server fix was not applied correctly.")
    elif server_result == "HUMAN_READABLE" and adk_result == "FAILED":
        print("\n❌ ISSUE IDENTIFIED: Server fixed but ADK integration broken!")
        print("   The issue is in the ADK MCP integration layer.")
    elif server_result == "HUMAN_READABLE" and adk_result == "SUCCESS":
        print("\n✅ Both server and ADK integration working!")
        print("   The spinning issue should be resolved.")
    else:
        print(f"\n⚠️  MIXED RESULTS: Server={server_result}, ADK={adk_result}")
        print("   Further investigation needed.")

if __name__ == "__main__":
    asyncio.run(main()) 