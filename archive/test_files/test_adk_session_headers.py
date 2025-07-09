#!/usr/bin/env python3
"""
Test to verify ADK session header expectations
"""

import requests
import json
import time

def test_adk_session_headers():
    """Test if server sends proper MCP-Session-Id headers"""
    print("🧪 Testing ADK Session Header Requirements")
    print("=" * 60)
    
    # Test 1: Check if SSE endpoint sends MCP-Session-Id header
    print("📡 Test 1: SSE endpoint header check...")
    
    try:
        response = requests.get('http://localhost:3000/mcp/sse', 
                               stream=True, 
                               headers={'Accept': 'text/event-stream'},
                               timeout=5)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        session_id = response.headers.get('MCP-Session-Id')
        if session_id:
            print(f"   ✅ MCP-Session-Id header found: {session_id}")
        else:
            print("   ❌ MCP-Session-Id header MISSING!")
            print("   This is likely why ADK times out!")
            return False
        
        # Read first few lines to see connection format
        lines = []
        for line in response.iter_lines(decode_unicode=True):
            lines.append(line)
            if len(lines) >= 3:
                break
        
        print("   First SSE events:")
        for i, line in enumerate(lines):
            print(f"     {i+1}. {line}")
            
    except Exception as e:
        print(f"   ❌ SSE connection failed: {e}")
        return False
    
    # Test 2: Check if POST endpoint expects MCP-Session-Id header
    print(f"\n📡 Test 2: POST endpoint session ID requirement...")
    
    # Test without session ID
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
        response_no_session = requests.post('http://localhost:3000/mcp',
                                           json=init_request,
                                           timeout=5)
        
        print(f"   Without session ID - Status: {response_no_session.status_code}")
        print(f"   Without session ID - Response: {response_no_session.text}")
        
        # Test with session ID
        response_with_session = requests.post('http://localhost:3000/mcp',
                                             json=init_request,
                                             headers={'MCP-Session-Id': session_id},
                                             timeout=5)
        
        print(f"   With session ID - Status: {response_with_session.status_code}")
        print(f"   With session ID - Response: {response_with_session.text}")
        
    except Exception as e:
        print(f"   ❌ POST test failed: {e}")
        return False
    
    # Test 3: Check if server actually uses the session ID
    print(f"\n📡 Test 3: Session ID validation...")
    
    # Try with invalid session ID
    try:
        response_invalid = requests.post('http://localhost:3000/mcp',
                                        json=init_request,
                                        headers={'MCP-Session-Id': 'invalid-session-id'},
                                        timeout=5)
        
        print(f"   Invalid session ID - Status: {response_invalid.status_code}")
        print(f"   Invalid session ID - Response: {response_invalid.text}")
        
        # If server properly validates session IDs, this should fail
        if response_invalid.status_code == 400:
            print("   ✅ Server properly validates session IDs")
        else:
            print("   ⚠️  Server doesn't validate session IDs")
            
    except Exception as e:
        print(f"   ❌ Session validation test failed: {e}")
        return False
    
    print(f"\n📋 Analysis:")
    print(f"   Session ID header: {'✅ Present' if session_id else '❌ Missing'}")
    print(f"   This is likely the cause of ADK timeout!")
    
    return session_id is not None

if __name__ == "__main__":
    success = test_adk_session_headers()
    if success:
        print("\n✅ Session headers working - issue is elsewhere")
    else:
        print("\n❌ Session headers broken - this is the ADK timeout cause")
    exit(0 if success else 1) 