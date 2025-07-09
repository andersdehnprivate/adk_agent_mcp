#!/usr/bin/env python3
import httpx
import time

def test_mcp_sse_endpoint():
    """Test the MCP SSE endpoint directly"""
    print("Testing MCP SSE endpoint...")
    
    url = "http://localhost:3000/mcp/sse"
    
    try:
        print(f"GET request to: {url}")
        start_time = time.time()
        
        # Try with a short timeout
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            
        end_time = time.time()
        print(f"Response time: {end_time - start_time:.2f}s")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:200]}...")
        
        return True
        
    except httpx.TimeoutException:
        print("❌ TIMEOUT: The /mcp/sse endpoint is not responding")
        print("This is why the ADK web interface hangs when starting a chat")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_mcp_sse_endpoint() 