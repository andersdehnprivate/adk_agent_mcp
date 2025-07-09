#!/usr/bin/env python3
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sse_streaming():
    """Test SSE streaming like ADK does"""
    print("Testing SSE streaming connection...")
    
    try:
        import requests
        
        # Test with streaming like ADK does
        print("1. Testing health endpoint...")
        r = requests.get('http://localhost:3000/health', timeout=5)
        print(f"   Health: {r.status_code}")
        
        print("2. Testing SSE endpoint with streaming...")
        response = requests.get('http://localhost:3000/mcp/sse', 
                              stream=True, 
                              timeout=5,
                              headers={'Accept': 'text/event-stream'})
        
        print(f"   SSE Status: {response.status_code}")
        print(f"   SSE Headers: {dict(response.headers)}")
        
        # Read a few SSE events
        print("3. Reading SSE events...")
        events_read = 0
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"   Event: {decoded_line}")
                events_read += 1
                if events_read >= 3:  # Read first 3 events
                    break
        
        print(f"   Successfully read {events_read} SSE events")
        response.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test actual ADK agent creation"""
    print("\nTesting ADK agent creation...")
    
    try:
        # First test SSE streaming
        if not test_sse_streaming():
            print("❌ SSE streaming test failed")
            return False
            
        print("4. Testing agent import...")
        sys.path.insert(0, '.')
        from agents.billy_agent.agent import create_mcp_agent
        
        print("5. Creating agent...")
        start_time = time.time()
        agent = create_mcp_agent()
        creation_time = time.time() - start_time
        
        print(f"   ✅ Agent created in {creation_time:.2f}s")
        print(f"   Agent name: {agent.name}")
        print(f"   Agent tools: {len(agent.tools)}")
        
        # List tool names
        if hasattr(agent, 'tools') and agent.tools:
            print("   Available tools:")
            for tool in agent.tools:
                print(f"     - {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_creation()
    if success:
        print("\n🎉 All tests passed! ADK-MCP integration is working!")
    else:
        print("\n❌ Tests failed - ADK-MCP integration needs more work") 