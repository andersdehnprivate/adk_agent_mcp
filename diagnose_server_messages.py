#!/usr/bin/env python3
"""
Diagnostic script to capture and display exact messages from MCP server
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def diagnose_mcp_server():
    """Connect to MCP server and capture all messages"""
    
    print("🔍 Diagnosing MCP Server Messages")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Connecting to http://localhost:3000/mcp/sse")
            
            async with session.get(
                'http://localhost:3000/mcp/sse',
                headers={
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            ) as response:
                
                print(f"📊 Status: {response.status}")
                print(f"📊 Headers: {dict(response.headers)}")
                print()
                
                if response.status != 200:
                    print(f"❌ Connection failed with status {response.status}")
                    return
                
                print("📨 Messages received:")
                print("-" * 30)
                
                message_count = 0
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    
                    print(f"[{timestamp}] Message #{message_count}:")
                    print(f"Raw: {repr(line)}")
                    
                    # Parse SSE format
                    if line.startswith('data: '):
                        data_part = line[6:]  # Remove 'data: ' prefix
                        print(f"Data: {data_part}")
                        
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(data_part)
                            print(f"JSON: {json.dumps(parsed, indent=2)}")
                            
                            # Check if it's valid JSON-RPC 2.0
                            required_fields = ['jsonrpc']
                            missing_fields = [field for field in required_fields if field not in parsed]
                            
                            if missing_fields:
                                print(f"❌ Missing JSON-RPC 2.0 fields: {missing_fields}")
                            else:
                                print("✅ Valid JSON-RPC 2.0 format")
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid JSON: {e}")
                            
                    elif line.startswith('event: '):
                        event_type = line[7:]  # Remove 'event: ' prefix
                        print(f"Event: {event_type}")
                        
                    elif line.startswith(':'):
                        print(f"Comment: {line}")
                        
                    else:
                        print(f"Other: {line}")
                    
                    print()
                    
                    # Stop after 10 messages or 10 seconds
                    if message_count >= 10:
                        print("🛑 Stopping after 10 messages")
                        break
                        
    except asyncio.TimeoutError:
        print("⏱️ Connection timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 WHAT THIS MEANS:")
    print("- If you see 'Missing JSON-RPC 2.0 fields', the server needs to send proper JSON-RPC messages")
    print("- Check MCP_SERVER_FIX_SPECIFICATION.md section 'Fix 1: SSE Protocol Implementation'")
    print("- The server should send messages like: {'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}}")

if __name__ == "__main__":
    # Run with timeout
    asyncio.run(asyncio.wait_for(diagnose_mcp_server(), timeout=10.0)) 