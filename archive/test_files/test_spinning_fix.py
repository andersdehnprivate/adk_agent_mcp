#!/usr/bin/env python3
"""
Test if the spinning fix is working
"""

import sys
import asyncio
import json
import requests

# Add paths
sys.path.append('.')
sys.path.insert(0, 'venv/Lib/site-packages')

def test_raw_billy_response():
    """Test what Billy.dk actually returns"""
    print('🔍 Testing raw Billy.dk response...')
    
    try:
        # Get SSE connection
        sse_response = requests.get('http://localhost:3000/mcp/sse', 
                                   headers={'Accept': 'text/event-stream'}, 
                                   stream=True, timeout=5)
        
        session_id = sse_response.headers.get('MCP-Session-Id')
        print(f'✅ SSE Session: {session_id}')
        
        # Send tool request
        tool_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'listInvoices',
                'arguments': {}
            }
        }
        
        post_response = requests.post('http://localhost:3000/mcp',
                                    json=tool_request,
                                    headers={'MCP-Session-Id': session_id})
        
        print(f'📋 POST Status: {post_response.status_code}')
        
        # Read SSE response
        raw_text = None
        for line in sse_response.iter_lines(decode_unicode=True):
            if line.strip() and 'result' in line:
                try:
                    if line.startswith('data: '):
                        data = line[6:]
                        parsed = json.loads(data)
                        if 'result' in parsed and 'content' in parsed['result']:
                            content = parsed['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                raw_text = content[0].get('text', '')
                                break
                except:
                    pass
        
        sse_response.close()
        
        if raw_text:
            print(f'✅ Got raw response: {len(raw_text)} chars')
            print(f'📋 Starts with: {raw_text[:50]}...')
            
            # Test if it's JSON
            stripped = raw_text.strip()
            if stripped.startswith('[') or stripped.startswith('{'):
                print('✅ Response is JSON')
                return raw_text
            else:
                print('❌ Response is not JSON')
                return None
        else:
            print('❌ No response received')
            return None
            
    except Exception as e:
        print(f'❌ Billy.dk test failed: {e}')
        return None

async def test_adk_formatting():
    """Test if ADK applies formatting"""
    print('\n🔍 Testing ADK formatting...')
    
    try:
        from billy_agent.agent import create_mcp_agent
        
        agent = create_mcp_agent()
        mcp_toolset = agent.tools[0]
        
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
            
            from google.adk.tools.tool_context import ToolContext
            tool_context = ToolContext()
            
            # Call the tool
            result = await list_invoices_tool._run_async_impl(
                args={},
                tool_context=tool_context,
                credential=None
            )
            
            if hasattr(result, 'content') and result.content:
                text = result.content[0].text
                print(f'📋 ADK result: {len(text)} chars')
                print(f'📋 Starts with: {text[:50]}...')
                
                if text.startswith('📋 Found'):
                    print('✅ SUCCESS! ADK applies formatting')
                    return True
                elif text.startswith('[') or text.startswith('{'):
                    print('❌ FAILED! ADK returns raw JSON')
                    return False
                else:
                    print(f'❓ UNCLEAR! Result: {text[:100]}...')
                    return False
            else:
                print('❌ No content in ADK result')
                return False
                
        else:
            print('❌ listInvoices tool not found')
            return False
            
    except Exception as e:
        print(f'❌ ADK test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    print('🚀 TESTING SPINNING FIX')
    print('=' * 40)
    
    # Test 1: Raw Billy.dk response
    raw_response = test_raw_billy_response()
    
    if raw_response:
        # Test 2: ADK formatting
        adk_result = asyncio.run(test_adk_formatting())
        
        if adk_result:
            print('\n🎉 SPINNING FIX IS WORKING!')
            print('✅ Billy.dk responses are properly formatted')
        else:
            print('\n❌ SPINNING FIX IS NOT WORKING')
            print('❌ ADK is still receiving raw JSON')
    else:
        print('\n❌ Billy.dk server not working')

if __name__ == '__main__':
    main() 