#!/usr/bin/env python3
"""
Final test to verify MCP tools are working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mcp_tools():
    """Test MCP tools functionality"""
    print("Final MCP Integration Test")
    print("=" * 40)
    
    # Test 1: Check environment
    print("\n1. Environment Check:")
    mcp_url = os.getenv("MCP_SERVER_URL")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"   MCP_SERVER_URL: {mcp_url}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    
    if not mcp_url:
        print("   ❌ MCP_SERVER_URL not set")
        return False
    
    if not openai_key:
        print("   ❌ OPENAI_API_KEY not set")
        return False
    
    # Test 2: Import and create agent
    print("\n2. Agent Creation:")
    try:
        from agents.mcp_agent.agent import root_agent
        print("   ✅ Agent imported successfully")
        
        # Check if agent has tools
        if hasattr(root_agent, 'tools') and root_agent.tools:
            print(f"   ✅ Agent has {len(root_agent.tools)} tools")
            
            # Check if MCP toolset is present
            for tool in root_agent.tools:
                tool_type = type(tool).__name__
                print(f"   - Tool type: {tool_type}")
                
                if 'MCP' in tool_type:
                    print("   ✅ MCP toolset found!")
                    return True
            
            print("   ⚠️  MCP toolset not found in tools")
            return False
        else:
            print("   ❌ Agent has no tools")
            return False
            
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the final test"""
    success = test_mcp_tools()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: MCP integration is working!")
        print("\nNext steps:")
        print("1. Start the web interface: python -m google.adk.ui.web")
        print("2. Or use the console interface: python agent_with_mcp.py")
        print("3. Test MCP tools by asking about invoices or customers")
    else:
        print("❌ FAILED: MCP integration has issues")
        print("\nPlease check:")
        print("1. MCP server is running on localhost:3000")
        print("2. Environment variables are set correctly")
        print("3. Dependencies are installed")

if __name__ == "__main__":
    main() 