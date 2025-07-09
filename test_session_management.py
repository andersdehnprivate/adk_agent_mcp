#!/usr/bin/env python3
"""
Test to verify server session management is working
"""

import requests
import json
import threading
import time
from queue import Queue

def test_session_management():
    """Test if server properly sends responses via SSE"""
    print("🧪 Testing Server Session Management")
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
                                  timeout=30)
            
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
    
    print(f"\n📤 Sending POST request with session: {session_id}")
    
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
                                    timeout=5)
        
        print(f"📋 POST status: {post_response.status_code}")
        print(f"📋 POST response: {post_response.text}")
        
        # Check POST response
        post_data = post_response.json()
        
        if (post_data.get("result", {}).get("status") == "message_sent_via_sse" or
            post_data.get("result", {}).get("status") == "sent"):
            print("✅ Server acknowledges message sent")
        else:
            print(f"⚠️ Unexpected POST response: {post_data}")
        
    except Exception as e:
        print(f"❌ POST request failed: {e}")
        return False
    
    # Wait for SSE response
    print("\n⏳ Waiting for initialization response via SSE...")
    
    # Look for initialization response in SSE messages
    initialization_received = False
    timeout = time.time() + 10  # 10 second timeout
    
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
                            parsed.get('id') == 1 and 
                            'result' in parsed and
                            'protocolVersion' in parsed.get('result', {})):
                            
                            print("✅ INITIALIZATION RESPONSE RECEIVED VIA SSE!")
                            print(f"   Data: {json.dumps(parsed, indent=2)}")
                            initialization_received = True
                            break
                    except json.JSONDecodeError:
                        pass
            
            if initialization_received:
                break
                
            time.sleep(0.1)
            
        except:
            break
    
    if initialization_received:
        print("\n🎉 SESSION MANAGEMENT IS WORKING!")
        print("✅ Server properly sends responses via SSE")
        print("✅ Chat should stop spinning")
        return True
    else:
        print("\n❌ SESSION MANAGEMENT IS NOT WORKING")
        print("❌ No initialization response received via SSE")
        print("❌ Server needs to implement session management")
        return False

if __name__ == "__main__":
    success = test_session_management()
    if success:
        print("\n🚀 READY TO USE: MCP integration should work in web interface!")
    else:
        print("\n🔧 FIX NEEDED: Implement session management on server")
    exit(0 if success else 1) 