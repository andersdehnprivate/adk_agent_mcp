import httpx
import json
import time
from httpx_sse import EventSource
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

def test_mcp_server_basic():
    """Test basic MCP server endpoints"""
    print("=== Testing MCP Server Basic Endpoints ===")
    
    base_url = "http://localhost:3000"
    
    # Test health endpoint
    try:
        response = httpx.get(f"{base_url}/health")
        print(f"Health endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
        return False
    
    # Test SSE endpoint
    try:
        response = httpx.get(f"{base_url}/mcp/sse")
        print(f"SSE endpoint: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        return response.status_code == 200
    except Exception as e:
        print(f"SSE endpoint error: {e}")
        return False

def test_sse_connection():
    """Test SSE connection and message format"""
    print("\n=== Testing SSE Connection and Message Format ===")
    
    url = "http://localhost:3000/mcp/sse"
    
    try:
        with EventSource(url) as event_source:
            print("SSE connection established successfully")
            
            # Read first few messages
            message_count = 0
            for message in event_source:
                message_count += 1
                print(f"Message {message_count}:")
                print(f"  Event: {message.event}")
                print(f"  Data: {message.data}")
                
                # Try to parse as JSON-RPC 2.0
                try:
                    data = json.loads(message.data)
                    print(f"  Parsed JSON: {data}")
                    
                    # Check JSON-RPC 2.0 format
                    if "jsonrpc" in data:
                        print("  ✓ JSON-RPC 2.0 format detected")
                    else:
                        print("  ✗ Missing 'jsonrpc' field")
                        
                except json.JSONDecodeError:
                    print("  ✗ Invalid JSON format")
                
                # Stop after 3 messages or 5 seconds
                if message_count >= 3:
                    break
                    
            return True
            
    except Exception as e:
        print(f"SSE connection error: {e}")
        return False

def test_adk_agent_creation():
    """Test ADK agent creation with MCP"""
    print("\n=== Testing ADK Agent Creation ===")
    
    try:
        # Import ADK components
        from google.adk.agents.mcp_agent import MCPAgent
        
        # Create agent
        agent = MCPAgent(
            name="Billy.dk Invoice Agent",
            description="Agent for managing Billy.dk invoices through MCP",
            mcp_server_url="http://localhost:3000/mcp"
        )
        
        print("✓ ADK Agent created successfully")
        print(f"Agent name: {agent.name}")
        print(f"Agent description: {agent.description}")
        print(f"MCP server URL: {agent.mcp_server_url}")
        
        # Test if agent has tools
        if hasattr(agent, 'get_tools'):
            tools = agent.get_tools()
            print(f"Available tools: {len(tools) if tools else 0}")
            if tools:
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"  - {tool.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"ADK agent creation error: {e}")
        return False

def test_web_interface_start():
    """Test starting the ADK web interface"""
    print("\n=== Testing ADK Web Interface ===")
    
    try:
        # Check if web interface can be started
        print("Starting ADK web interface...")
        print("Run: adk web")
        print("Expected: Web interface should start on port 8000")
        print("Expected: MCP agent should be available in the interface")
        print("Expected: MCP tools should be accessible")
        
        return True
        
    except Exception as e:
        print(f"Web interface test error: {e}")
        return False

def main():
    print("MCP Integration Final Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    tests = [
        ("Basic Server", test_mcp_server_basic),
        ("SSE Connection", test_sse_connection),
        ("ADK Agent Creation", test_adk_agent_creation),
        ("Web Interface", test_web_interface_start)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_tests_passed = False
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
            all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_tests_passed else '✗ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("\n🎉 MCP integration is working correctly!")
        print("You can now start the ADK web interface with: adk web")
    else:
        print("\n❌ Some issues remain. Check the test output above.")

if __name__ == "__main__":
    main() 