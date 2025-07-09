import httpx
import json

def test_sse_endpoint():
    """Test SSE endpoint"""
    print("Testing SSE endpoint...")
    
    try:
        response = httpx.get('http://localhost:3000/mcp/sse', timeout=3)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response: {response.text[:200]}...")
        return True
    except httpx.TimeoutException:
        print("SSE endpoint timed out")
        return False
    except Exception as e:
        print(f"SSE endpoint error: {e}")
        return False

def test_adk_import():
    """Test ADK import paths"""
    print("\nTesting ADK import paths...")
    
    import_paths = [
        "google.adk.agents.mcp_agent",
        "google.adk.agents", 
        "google.adk",
        "adk.agents.mcp_agent",
        "adk.agents",
        "adk"
    ]
    
    for path in import_paths:
        try:
            __import__(path)
            print(f"✓ {path} - SUCCESS")
        except ImportError as e:
            print(f"✗ {path} - FAILED: {e}")
    
    # Try to find the correct agent class
    print("\nLooking for agent classes...")
    try:
        import adk
        print(f"ADK module: {adk}")
        print(f"ADK dir: {dir(adk)}")
    except:
        pass
    
    try:
        from agents.mcp_agent import MCPAgent
        print("✓ Found MCPAgent in agents.mcp_agent")
        return True
    except ImportError:
        print("✗ MCPAgent not found in agents.mcp_agent")
    
    return False

if __name__ == "__main__":
    test_sse_endpoint()
    test_adk_import() 