#!/usr/bin/env python3
"""
Test script to verify the updated MCP server endpoints
"""

import requests
import json
import sys

def test_mcp_endpoints():
    """Test the MCP server endpoints"""
    base_url = "http://localhost:3000"
    
    endpoints_to_test = [
        "/health",
        "/mcp", 
        "/mcp/sse"
    ]
    
    print("Testing MCP Server Endpoints")
    print("=" * 40)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                if response.headers.get('content-type', '').startswith('text/'):
                    print(f"Content preview: {response.text[:200]}...")
                elif response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"JSON response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"Response text: {response.text[:200]}...")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("Testing complete!")

if __name__ == "__main__":
    test_mcp_endpoints() 