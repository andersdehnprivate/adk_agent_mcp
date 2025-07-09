#!/usr/bin/env python3
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent_creation():
    """Test what happens during agent creation"""
    print("Testing agent creation process...")
    print(f"MCP_SERVER_URL: {os.getenv('MCP_SERVER_URL')}")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    
    try:
        print("1. Testing MCP server connection...")
        import httpx
        r = httpx.get('http://localhost:3000/health', timeout=3)
        print(f"   Health check: {r.status_code}")
        
        print("2. Testing SSE endpoint...")
        r = httpx.get('http://localhost:3000/mcp/sse', timeout=3)
        print(f"   SSE endpoint: {r.status_code} - {r.headers.get('content-type')}")
        
        print("3. Testing agent import...")
        sys.path.insert(0, '.')
        from agents.billy_agent.agent import create_mcp_agent
        
        print("4. Creating agent...")
        agent = create_mcp_agent()
        print(f"   Agent created: {agent.name}")
        print(f"   Agent tools: {len(agent.tools)}")
        
        print("5. Testing agent response...")
        # Don't actually send message as it might hang
        print("   Agent ready for interaction")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_creation() 