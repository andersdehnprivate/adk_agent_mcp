#!/usr/bin/env python3
"""
Diagnostic script to check MCP server endpoints
"""

import requests
import json

def test_endpoint(url, method='GET', data=None, headers=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        print(f"✅ {method} {url}: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:200]}...")
        return response.status_code
    except Exception as e:
        print(f"❌ {method} {url}: ERROR - {e}")
        return None

def diagnose_mcp_server():
    """Diagnose MCP server endpoints"""
    print("🔍 MCP Server Endpoint Diagnosis")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    
    # Test all possible endpoints
    endpoints = [
        "/",
        "/health",
        "/mcp",
        "/mcp/sse",
        "/mcp/health",
        "/messages",
        "/sse",
        "/api/mcp",
        "/api/mcp/sse"
    ]
    
    print("📊 Testing GET endpoints:")
    for endpoint in endpoints:
        test_endpoint(f"{base_url}{endpoint}")
    
    print("\n📊 Testing POST endpoints:")
    test_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05"
        }
    }
    
    for endpoint in ["/mcp", "/mcp/sse", "/api/mcp"]:
        test_endpoint(f"{base_url}{endpoint}", method='POST', data=test_data)
    
    print("\n🎯 What ADK expects:")
    print("   - GET /mcp/sse → SSE connection")
    print("   - POST /mcp → JSON-RPC requests")
    print("   - Both should work together")
    
    print("\n💡 If /mcp returns 404:")
    print("   - Server needs to implement POST /mcp endpoint")
    print("   - This is where ADK sends initialization and tool requests")

if __name__ == "__main__":
    diagnose_mcp_server() 