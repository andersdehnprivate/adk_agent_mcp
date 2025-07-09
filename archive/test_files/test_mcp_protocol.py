#!/usr/bin/env python3
import requests
import json
import time

def test_mcp_protocol_flow():
    """Test the complete MCP protocol flow like ADK does"""
    print("Testing MCP protocol flow...")
    
    try:
        # Step 1: Connect to SSE endpoint
        print("1. Connecting to SSE endpoint...")
        response = requests.get('http://localhost:3000/mcp/sse', 
                              stream=True, 
                              timeout=None,  # No timeout for SSE
                              headers={'Accept': 'text/event-stream'})
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Step 2: Read initial events with timeout
        print("2. Reading initial SSE events...")
        events = []
        start_time = time.time()
        
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"   Raw line: {repr(line)}")
                    events.append(line)
                    
                    # Check if we've been waiting too long
                    if time.time() - start_time > 10:  # 10 second timeout
                        print("   Timeout waiting for more events")
                        break
                        
                    # If we got some events, check if we have what we need
                    if len(events) >= 2:
                        print(f"   Got {len(events)} events, checking content...")
                        break
                        
        except Exception as e:
            print(f"   Error reading events: {e}")
            
        response.close()
        
        # Step 3: Analyze the events
        print("3. Analyzing events...")
        for i, event in enumerate(events):
            print(f"   Event {i}: {event}")
            
        # Step 4: Try to parse JSON-RPC messages
        print("4. Looking for JSON-RPC messages...")
        json_messages = []
        for event in events:
            if event.startswith('data: '):
                data_part = event[6:]  # Remove 'data: ' prefix
                try:
                    json_msg = json.loads(data_part)
                    json_messages.append(json_msg)
                    print(f"   JSON message: {json_msg}")
                except json.JSONDecodeError:
                    print(f"   Non-JSON data: {data_part}")
                    
        if json_messages:
            print(f"   Found {len(json_messages)} JSON-RPC messages")
            return True
        else:
            print("   No JSON-RPC messages found - this is the problem!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_mcp_initialization():
    """Test manual MCP initialization"""
    print("\nTesting manual MCP initialization...")
    
    try:
        # Try to send an initialization request
        print("1. Sending initialization request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "ADK",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post('http://localhost:3000/mcp', 
                               json=init_request,
                               timeout=5)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"   Parsed response: {json_response}")
                return True
            except json.JSONDecodeError:
                print("   Response is not valid JSON")
                return False
        else:
            print(f"   HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing MCP Protocol ===")
    
    sse_success = test_mcp_protocol_flow()
    post_success = test_manual_mcp_initialization()
    
    if sse_success and post_success:
        print("\n🎉 MCP protocol is working correctly!")
    else:
        print("\n❌ MCP protocol issues found:")
        if not sse_success:
            print("   - SSE endpoint not sending proper JSON-RPC messages")
        if not post_success:
            print("   - POST endpoint not handling initialization requests")
        print("\nThe MCP server needs to implement proper JSON-RPC 2.0 message flow") 