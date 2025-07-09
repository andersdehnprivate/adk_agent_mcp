#!/usr/bin/env python3
"""
Debug formatting issue
"""

import sys
import asyncio
import logging

# Add paths
sys.path.append('.')
sys.path.insert(0, 'venv/Lib/site-packages')

# Enable debug logging
logging.basicConfig(level=logging.INFO)

async def debug_tool_call():
    print('🔍 DEBUGGING ADK Tool Call...')
    
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
        
        if not list_invoices_tool:
            print('❌ listInvoices tool not found')
            return
        
        print(f'✅ Found listInvoices tool: {list_invoices_tool.name}')
        
        # Make the tool call
        from google.adk.tools.tool_context import ToolContext
        tool_context = ToolContext()
        
        print('📤 Calling tool...')
        result = await list_invoices_tool._run_async_impl(
            args={},
            tool_context=tool_context,
            credential=None
        )
        
        print('✅ Tool call completed')
        
        # Debug the response structure
        print(f'📋 Result type: {type(result)}')
        print(f'📋 Has content: {hasattr(result, "content")}')
        
        if hasattr(result, 'content'):
            print(f'📋 Content type: {type(result.content)}')
            print(f'📋 Content length: {len(result.content) if result.content else 0}')
            
            if result.content and len(result.content) > 0:
                first_item = result.content[0]
                print(f'📋 First item type: {type(first_item)}')
                print(f'📋 First item has text: {hasattr(first_item, "text")}')
                
                if hasattr(first_item, 'text'):
                    text = first_item.text
                    print(f'📋 Text length: {len(text)}')
                    print(f'📋 Text starts with: {repr(text[:50])}')
                    
                    # Check what our logic would do
                    stripped = text.strip()
                    starts_with_bracket = stripped.startswith('[')
                    starts_with_brace = stripped.startswith('{')
                    
                    print(f'📋 Stripped starts with [: {starts_with_bracket}')
                    print(f'📋 Stripped starts with {{: {starts_with_brace}')
                    
                    if starts_with_bracket or starts_with_brace:
                        print('✅ Text looks like JSON - formatting should have been applied')
                        
                        # Check if it was formatted
                        if text.startswith('📋 Found'):
                            print('🎉 SUCCESS! Text was formatted!')
                        else:
                            print('❌ PROBLEM! Text was not formatted despite being JSON')
                            print(f'❌ First 200 chars: {text[:200]}...')
                    else:
                        print('❌ Text does not look like JSON')
                        print(f'❌ First 200 chars: {text[:200]}...')
                else:
                    print('❌ First item has no text attribute')
            else:
                print('❌ No content items')
        else:
            print('❌ Result has no content attribute')
            
    except Exception as e:
        print(f'❌ Debug failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(debug_tool_call()) 