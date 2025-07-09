#!/usr/bin/env python3
import requests
import json
import time
import threading
import sys

def diagnose_mcp_server():
    """Diagnose exactly what the MCP server is sending"""
    print("🔍 Diagnosing MCP Server Communication...")
    
    try:
        print("1. Connecting to SSE endpoint...")
        response = requests.get('http://localhost:3000/mcp/sse', 
                              stream=True, 
                              timeout=2,  # 2 second connection timeout
                              headers={'Accept': 'text/event-stream'})
        
        print(f"   ✅ Connected: {response.status_code}")
        print(f"   Headers: {response.headers.get('content-type')}")
        
        print("\n2. Reading SSE stream (5 second timeout)...")
        event_count = 0
        start_time = time.time()
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                event_count += 1
                print(f"   Event {event_count}: {repr(line)}")
                
                # Check if it's an SSE data event
                if line.startswith('data: '):
                    data_part = line[6:]
                    try:
                        json_msg = json.loads(data_part)
                        print(f"   📄 JSON: {json_msg}")
                    except json.JSONDecodeError:
                        print(f"   📝 Raw data: {data_part}")
                        
            # Check timeout
            if time.time() - start_time > 5:
                print("\n⏰ Timeout reached - no more events received")
                break
                
        print("\n3. Stream processing completed")
        
    except requests.exceptions.ReadTimeout:
        print("\n⏰ Connection timed out")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    print(f"\n📊 Summary: Received {event_count} events")
    if event_count == 0:
        print("   🚨 No events received - server not responding")
    elif event_count == 1:
        print("   ⚠️  Only connection event - no MCP protocol messages")
    else:
        print("   ✅ Multiple events received")

def test_post_endpoint():
    """Test the POST endpoint separately"""
    print("\n🔍 Testing POST endpoint...")
    
    try:
        # Test basic POST
        response = requests.post('http://localhost:3000/mcp', 
                               json={"test": "data"},
                               timeout=3)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Test MCP initialization
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        response = requests.post('http://localhost:3000/mcp', 
                               json=init_msg,
                               timeout=3)
        
        print(f"   Init Status: {response.status_code}")
        print(f"   Init Response: {response.text}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 MCP Server Diagnostic Tool")
    print("=" * 50)
    
    diagnose_mcp_server()
    test_post_endpoint()
    
    print("\n" + "=" * 50)
    print("💡 Expected behavior:")
    print("   - SSE should send JSON-RPC 2.0 messages")
    print("   - POST should handle initialization requests")
    print("   - Both endpoints should work for full MCP protocol")
    print("=" * 50) 