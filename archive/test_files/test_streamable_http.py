#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_streamable_http_mcp():
    """Test MCP server using Streamable HTTP protocol"""
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
    session_id = "adk-test-session-123"
    
    print(f"🧪 Testing Streamable HTTP MCP Protocol")
    print(f"🔗 Server URL: {mcp_url}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Initialize the MCP session
        print("📡 Step 1: Initializing MCP session...")
        
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "adk-test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }
        
        try:
            async with session.post(mcp_url, 
                                  json=init_request, 
                                  headers=headers) as response:
                print(f"   Status: {response.status}")
                text = await response.text()
                print(f"   Response: {text}")
                
                if response.status == 200:
                    init_result = json.loads(text)
                    if "result" in init_result:
                        print("   ✅ Initialization successful!")
                        
                        # Step 2: Send initialized notification
                        print("📡 Step 2: Sending initialized notification...")
                        
                        initialized_notification = {
                            "jsonrpc": "2.0",
                            "method": "initialized",
                            "params": {}
                        }
                        
                        async with session.post(mcp_url,
                                              json=initialized_notification,
                                              headers=headers) as notif_response:
                            print(f"   Status: {notif_response.status}")
                            
                            if notif_response.status == 200:
                                print("   ✅ Initialized notification sent!")
                                
                                # Step 3: List available tools
                                print("📡 Step 3: Listing available tools...")
                                
                                tools_request = {
                                    "jsonrpc": "2.0",
                                    "method": "tools/list",
                                    "id": 2
                                }
                                
                                async with session.post(mcp_url,
                                                      json=tools_request,
                                                      headers=headers) as tools_response:
                                    print(f"   Status: {tools_response.status}")
                                    tools_text = await tools_response.text()
                                    print(f"   Response: {tools_text}")
                                    
                                    if tools_response.status == 200:
                                        tools_result = json.loads(tools_text)
                                        if "result" in tools_result and "tools" in tools_result["result"]:
                                            tools = tools_result["result"]["tools"]
                                            print(f"   ✅ Found {len(tools)} tools:")
                                            for i, tool in enumerate(tools, 1):
                                                print(f"      {i}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                                            return True
                                        else:
                                            print("   ❌ Invalid tools response format")
                                    else:
                                        print("   ❌ Failed to list tools")
                            else:
                                print("   ❌ Failed to send initialized notification")
                    else:
                        print(f"   ❌ Initialization failed: {init_result}")
                else:
                    print(f"   ❌ HTTP {response.status}: {text}")
                    
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    return False

async def main():
    success = await test_streamable_http_mcp()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    if success:
        print("✅ Streamable HTTP MCP protocol is working!")
        print("🔧 Your server supports the current MCP standard.")
        print("💡 Next: Update ADK configuration to use this protocol.")
    else:
        print("❌ Streamable HTTP test failed.")
        print("🔧 Server may need configuration updates.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 