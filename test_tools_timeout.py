#!/usr/bin/env python3
"""
Test specifically for MCP tools timeout issue
"""

import requests
import json
import threading
import time
from queue import Queue

def test_tools_timeout():
    """Test tools/list specifically to diagnose timeout"""
    print("🧪 Testing MCP Tools Timeout Issue")
    print("=" * 50)
    
    # Queue to collect SSE messages
    sse_messages = Queue()
    session_id = None
    
    def sse_listener():
        """Listen for SSE messages"""
        nonlocal session_id
        try:
            response = requests.get('http://localhost:3000/mcp/sse', 
                                  stream=True, 
                                  headers={'Accept': 'text/event-stream'},
                                  timeout=60)
            
            # Get session ID from headers
            session_id = response.headers.get('MCP-Session-Id')
            print(f"📡 SSE connected with session: {session_id}")
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    sse_messages.put(line)
                    print(f"📨 SSE received: {line}")
                    
        except Exception as e:
            print(f"❌ SSE error: {e}")
    
    # Start SSE listener in background
    sse_thread = threading.Thread(target=sse_listener)
    sse_thread.daemon = True
    sse_thread.start()
    
    # Wait for connection and session ID
    time.sleep(2)
    
    if not session_id:
        print("❌ Failed to get session ID from SSE connection")
        return False
    
    print(f"\n📤 Step 1: Sending initialization request...")
    
    # Send initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
    }
    
    try:
        post_response = requests.post('http://localhost:3000/mcp',
                                    json=init_request,
                                    headers={'MCP-Session-Id': session_id},
                                    timeout=10)
        
        print(f"📋 Init POST status: {post_response.status_code}")
        print(f"📋 Init POST response: {post_response.text}")
        
        # Wait for initialization response
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Initialization POST failed: {e}")
        return False
    
    print(f"\n📤 Step 2: Sending tools/list request...")
    
    # Send tools/list request  
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        tools_response = requests.post('http://localhost:3000/mcp',
                                     json=tools_request,
                                     headers={'MCP-Session-Id': session_id},
                                     timeout=10)
        
        print(f"📋 Tools POST status: {tools_response.status_code}")
        print(f"📋 Tools POST response: {tools_response.text}")
        
    except Exception as e:
        print(f"❌ Tools POST failed: {e}")
        return False
    
    print(f"\n⏳ Step 3: Waiting for tools/list response via SSE...")
    
    # Wait for tools response
    tools_response_received = False
    timeout = time.time() + 15  # 15 second timeout
    
    while time.time() < timeout:
        try:
            # Check if we have messages
            while not sse_messages.empty():
                message = sse_messages.get_nowait()
                
                if message.startswith('data: '):
                    data_part = message[6:]
                    try:
                        parsed = json.loads(data_part)
                        if (parsed.get('jsonrpc') == '2.0' and 
                            parsed.get('id') == 2 and
                            'result' in parsed):
                            
                            print("✅ TOOLS RESPONSE RECEIVED VIA SSE!")
                            print(f"   Data: {json.dumps(parsed, indent=2)}")
                            tools_response_received = True
                            break
                    except json.JSONDecodeError:
                        pass
            
            if tools_response_received:
                break
                
            time.sleep(0.1)
            
        except:
            break
    
    if tools_response_received:
        print("\n🎉 TOOLS ARE WORKING!")
        print("✅ Server properly sends tools/list response via SSE")
        return True
    else:
        print("\n❌ TOOLS TIMEOUT CONFIRMED")
        print("❌ No tools/list response received via SSE")
        print("❌ Server may not implement tools/list method properly")
        
        # Show what we did receive
        print("\n📋 Messages received during test:")
        remaining_messages = []
        while not sse_messages.empty():
            remaining_messages.append(sse_messages.get_nowait())
        
        for msg in remaining_messages:
            print(f"   {msg}")
            
        return False

if __name__ == "__main__":
    success = test_tools_timeout()
    if success:
        print("\n🚀 TOOLS WORKING: MCP integration fully functional!")
    else:
        print("\n🔧 TOOLS TIMEOUT: Server needs tools/list implementation")
    exit(0 if success else 1) 