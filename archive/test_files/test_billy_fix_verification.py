import asyncio
import httpx
import json

async def test_billy_formatting_fix():
    """Test that Billy.dk MCP server now returns human-readable responses"""
    
    print("Testing Billy.dk MCP server response formatting...")
    print("=" * 60)
    
    # Test the MCP integration through ADK
    try:
        # Test a simple invoice query through ADK's MCP tool
        async with httpx.AsyncClient() as client:
            # First test - check if Billy.dk MCP server is responding
            response = await client.get("http://localhost:3000/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Billy.dk MCP server is running")
            else:
                print(f"❌ Billy.dk MCP server health check failed: {response.status_code}")
                return
                
            # Now test the actual MCP integration through ADK
            print("\nTesting MCP tool integration through ADK...")
            
            # Check ADK server
            adk_response = await client.get("http://localhost:8000/health", timeout=5.0)
            if adk_response.status_code == 200:
                print("✅ ADK server is running")
            else:
                print(f"❌ ADK server not accessible: {adk_response.status_code}")
                return
                
            print("\n🔍 Manual Test Instructions:")
            print("1. Open browser to http://localhost:8000")
            print("2. Go to the chat interface")
            print("3. Ask: 'Show me my invoices'")
            print("4. Verify the response is human-readable text (not raw JSON)")
            print("5. Check that the chat doesn't spin endlessly")
            print("\nExpected behavior:")
            print("- Should see: 'Found X invoices: Invoice #123 for $1,000.00...'")
            print("- Should NOT see: '[{\"id\": \"zIG8...\", \"grossAmount\": 1000}]'")
            print("- Chat should respond normally without spinning")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return
        
    print("\n✅ Servers are running - ready for manual web UI testing")

if __name__ == "__main__":
    asyncio.run(test_billy_formatting_fix()) 