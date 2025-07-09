#!/usr/bin/env python3
"""
Test Billy.dk response formatting functionality
"""

import sys
import asyncio
import json

# Add paths
sys.path.append('.')
sys.path.insert(0, 'venv/Lib/site-packages')

async def test_billy_formatting():
    print('🔍 Testing Billy.dk Response Formatting')
    print('=' * 50)
    
    # Test 1: Test formatting function directly
    print('\n🧪 Test 1: Testing formatting function...')
    
    try:
        from google.adk.tools.mcp_tool.mcp_tool import format_billy_response
        
        # Test with sample data that mimics Billy.dk
        sample_data = [
            {
                'invoiceNo': '12345',
                'grossAmount': 1000,
                'currencyId': 'DKK',
                'invoiceDate': '2024-07-09',
                'state': 'approved',
                'contactId': 'customer123',
                'description': 'Test invoice'
            },
            {
                'invoiceNo': '67890',
                'grossAmount': 2500,
                'currencyId': 'DKK',
                'invoiceDate': '2024-07-08',
                'state': 'draft',
                'contactId': 'customer456',
                'description': 'Another test invoice'
            }
        ]
        
        formatted = format_billy_response(sample_data)
        print(f'✅ Format function completed')
        print(f'📋 Formatted output:\n{formatted}')
        
        if formatted.startswith('📋 Found'):
            print('✅ Formatting produces correct output')
        else:
            print('❌ Formatting produces incorrect output')
            
    except Exception as e:
        print(f'❌ Format function test failed: {e}')
        import traceback
        traceback.print_exc()
        return False
        
    # Test 2: Test with real ADK MCP tool
    print('\n🧪 Test 2: Testing real ADK MCP tool...')
    
    try:
        from billy_agent.agent import create_mcp_agent
        
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
            
            # Test the tool call
            print('\n📤 Testing tool call...')
            
            from google.adk.tools.tool_context import ToolContext
            tool_context = ToolContext()
            
            result = await list_invoices_tool._run_async_impl(
                args={},
                tool_context=tool_context,
                credential=None
            )
            
            if hasattr(result, 'content') and result.content:
                text = result.content[0].text
                print(f'📋 Response length: {len(text)}')
                print(f'📋 Response starts with: {text[:100]}...')
                
                if text.startswith('📋 Found'):
                    print('\n🎉 SUCCESS! Billy.dk response is now formatted!')
                    print('✅ The formatting fix is working correctly!')
                    return True
                else:
                    print('\n❌ Response is still not formatted')
                    print(f'❌ Response: {text[:200]}...')
                    return False
            else:
                print('❌ No content in response')
                return False
                
        else:
            print('❌ listInvoices tool not found')
            return False
            
    except Exception as e:
        print(f'❌ ADK test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_billy_formatting())
    print(f'\n📊 Formatting fix test: {"SUCCESS" if result else "FAILED"}') 