#!/usr/bin/env python3
import asyncio
import httpx
import json
import uuid
from httpx_sse import aconnect_sse
from datetime import datetime

async def test_billy_mcp_response_format():
    """Test Billy.dk MCP server response format through SSE"""
    print("🔍 Testing Billy.dk MCP Server Response Format")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    try:
        # Test 1: Test SSE connection
        print("1. Testing SSE connection...")
        async with httpx.AsyncClient() as client:
            url = "http://localhost:3000/mcp/sse"
            headers = {"MCP-Session-Id": session_id}
            
            async with aconnect_sse(client, "GET", url, headers=headers) as event_source:
                print("   ✅ SSE connection established")
                
                # Test 2: Send initialization message
                print("\n2. Sending MCP initialization...")
                init_message = {
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
                
                # Send initialization via POST
                init_response = await client.post(
                    "http://localhost:3000/mcp/message",
                    json=init_message,
                    headers=headers
                )
                
                if init_response.status_code == 200:
                    print("   ✅ Initialization sent successfully")
                else:
                    print(f"   ❌ Initialization failed: {init_response.status_code}")
                    print(f"   Response: {init_response.text}")
                    return "INIT_FAILED"
                
                # Test 3: Listen for responses
                print("\n3. Listening for responses...")
                message_count = 0
                async for sse_event in event_source:
                    message_count += 1
                    print(f"   Message {message_count}: {sse_event.data}")
                    
                    try:
                        data = json.loads(sse_event.data)
                        if data.get("id") == 1:  # Initialization response
                            print("   ✅ Received initialization response")
                            break
                    except json.JSONDecodeError:
                        print("   ⚠️  Non-JSON message received")
                    
                    if message_count >= 5:  # Safety limit
                        break
                
                # Test 4: Send tools list request
                print("\n4. Requesting tools list...")
                tools_message = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                tools_response = await client.post(
                    "http://localhost:3000/mcp/message",
                    json=tools_message,
                    headers=headers
                )
                
                if tools_response.status_code == 200:
                    print("   ✅ Tools list request sent")
                else:
                    print(f"   ❌ Tools list request failed: {tools_response.status_code}")
                    return "TOOLS_FAILED"
                
                # Listen for tools response
                tools_found = False
                async for sse_event in event_source:
                    message_count += 1
                    print(f"   Message {message_count}: {sse_event.data}")
                    
                    try:
                        data = json.loads(sse_event.data)
                        if data.get("id") == 2:  # Tools response
                            tools = data.get("result", {}).get("tools", [])
                            print(f"   ✅ Found {len(tools)} tools")
                            for tool in tools[:3]:  # Show first 3
                                print(f"     - {tool.get('name', 'Unknown')}")
                            tools_found = True
                            break
                    except json.JSONDecodeError:
                        pass
                    
                    if message_count >= 10:  # Safety limit
                        break
                
                if not tools_found:
                    print("   ❌ Tools list response not received")
                    return "NO_TOOLS"
                
                # Test 5: Call invoice tool to check response format
                print("\n5. Testing invoice tool response format...")
                invoice_message = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "get_invoices",
                        "arguments": {"limit": 2}
                    }
                }
                
                invoice_response = await client.post(
                    "http://localhost:3000/mcp/message",
                    json=invoice_message,
                    headers=headers
                )
                
                if invoice_response.status_code == 200:
                    print("   ✅ Invoice tool call sent")
                else:
                    print(f"   ❌ Invoice tool call failed: {invoice_response.status_code}")
                    return "INVOICE_FAILED"
                
                # Listen for invoice response
                async for sse_event in event_source:
                    message_count += 1
                    print(f"   Message {message_count}: {sse_event.data}")
                    
                    try:
                        data = json.loads(sse_event.data)
                        if data.get("id") == 3:  # Invoice response
                            print("   ✅ Received invoice response")
                            
                            # Check response format
                            result = data.get("result", {})
                            content = result.get("content", [])
                            
                            if content:
                                first_content = content[0]
                                content_text = first_content.get("text", "")
                                
                                print(f"\n   📋 Response Content (first 300 chars):")
                                print(f"   {content_text[:300]}...")
                                
                                # Check if it's raw JSON
                                try:
                                    parsed = json.loads(content_text)
                                    print("\n   ❌ ISSUE FOUND: Response is still raw JSON!")
                                    print(f"   First item keys: {list(parsed[0].keys()) if parsed else 'None'}")
                                    return "RAW_JSON"
                                except json.JSONDecodeError:
                                    print("\n   ✅ Response is human-readable text!")
                                    return "HUMAN_READABLE"
                            else:
                                print("   ❌ No content in response")
                                return "NO_CONTENT"
                            
                            break
                    except json.JSONDecodeError:
                        pass
                    
                    if message_count >= 15:  # Safety limit
                        break
                
                return "TIMEOUT"
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return "EXCEPTION"

async def test_adk_mcp_tool():
    """Test ADK MCP tool integration"""
    print("\n🔍 Testing ADK MCP Tool Integration")
    print("=" * 50)
    
    try:
        # Check if ADK has MCP tools configured
        print("1. Checking ADK MCP configuration...")
        
        # This is a placeholder - we need to find the actual ADK MCP tool endpoint
        async with httpx.AsyncClient() as client:
            # Try to find ADK's MCP tools endpoint
            endpoints_to_try = [
                "http://localhost:8000/api/tools",
                "http://localhost:8000/tools",
                "http://localhost:8000/mcp/tools",
                "http://localhost:8000/api/mcp/tools"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await client.get(endpoint, timeout=5.0)
                    if response.status_code == 200:
                        print(f"   ✅ Found ADK endpoint: {endpoint}")
                        data = response.json()
                        print(f"   Response: {data}")
                        return "SUCCESS"
                except Exception as e:
                    print(f"   ❌ {endpoint}: {e}")
            
            print("   ❌ No ADK MCP endpoints found")
            return "NO_ENDPOINT"
            
    except Exception as e:
        print(f"❌ ADK integration test failed: {e}")
        return "EXCEPTION"

async def main():
    """Run comprehensive tests"""
    print("🚀 Billy.dk MCP Response Format Testing")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Billy.dk MCP server response format
    billy_result = await test_billy_mcp_response_format()
    
    # Test 2: ADK MCP integration
    adk_result = await test_adk_mcp_tool()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 40)
    print(f"Billy.dk MCP Server Response: {billy_result}")
    print(f"ADK MCP Integration: {adk_result}")
    
    if billy_result == "RAW_JSON":
        print("\n❌ ISSUE IDENTIFIED: Billy.dk still returns raw JSON!")
        print("   The server fix was NOT applied correctly.")
        print("   This is causing the chat spinning issue.")
    elif billy_result == "HUMAN_READABLE":
        print("\n✅ Billy.dk server is fixed!")
        print("   It now returns human-readable responses.")
        if adk_result != "SUCCESS":
            print("   But ADK integration may have issues.")
    else:
        print(f"\n⚠️  Billy.dk test result: {billy_result}")
        print("   Further investigation needed.")

if __name__ == "__main__":
    asyncio.run(main()) 