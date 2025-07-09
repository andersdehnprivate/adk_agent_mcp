#!/usr/bin/env python3
"""
Test ADK MCP tool formatting
"""

import sys
import asyncio

# Add paths
sys.path.append('.')
sys.path.insert(0, 'venv/Lib/site-packages')

async def test_adk_tool():
    print('🔍 Testing ADK MCP Tool with Billy.dk...')
    
    try:
        from billy_agent.agent import create_mcp_agent
        
        # Create agent
        agent = create_mcp_agent()
        mcp_toolset = agent.tools[0]
        
        # Get tools
        tools = await mcp_toolset.get_tools()
        print(f'✅ Got {len(tools)} tools')
        
        # Find listInvoices tool
        list_invoices_tool = None
        for tool in tools:
            if tool.name == 'listInvoices':
                list_invoices_tool = tool
                break
        
        if list_invoices_tool:
            print(f'✅ Found listInvoices tool')
            
            # Test the tool call with formatting
            print('\n📤 Testing tool call...')
            
            from google.adk.tools.tool_context import ToolContext
            tool_context = ToolContext()
            
            # This should trigger the formatting
            result = await list_invoices_tool._run_async_impl(
                args={},
                tool_context=tool_context,
                credential=None
            )
            
            print(f'✅ Tool call completed')
            
            if hasattr(result, 'content') and result.content:
                text = result.content[0].text
                print(f'📋 Response length: {len(text)}')
                print(f'📋 Response starts with: {text[:100]}...')
                
                if text.startswith('📋 Found'):
                    print('\n🎉 SUCCESS! Formatting is applied!')
                    print('✅ Billy.dk response is now formatted for ADK')
                    return True
                elif text.startswith('['):
                    print('\n❌ Response is still raw JSON')
                    print('❌ Formatting is NOT being applied')
                    return False
                else:
                    print(f'\n❓ Unexpected response format: {text[:50]}...')
                    return False
            else:
                print('❌ No content in response')
                return False
                
        else:
            print('❌ listInvoices tool not found')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_adk_tool())
    status = "SUCCESS" if result else "FAILED"
    print(f'\n📊 ADK Tool Test: {status}') 