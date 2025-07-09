#!/usr/bin/env python3
import requests
import json
import time
import threading
from queue import Queue, Empty

def deep_analyze_connection():
    print('🔍 Deep Analysis of ADK Connection Issue')
    print('=' * 60)
    
    # Collect all SSE events
    sse_events = Queue()
    session_id = None
    connection_active = True
    
    def sse_monitor():
        nonlocal session_id, connection_active
        try:
            print('📡 Opening SSE connection...')
            response = requests.get('http://localhost:3000/mcp/sse', 
                                  stream=True, 
                                  headers={'Accept': 'text/event-stream'})
            
            session_id = response.headers.get('MCP-Session-Id')
            print(f'✅ SSE connected with session: {session_id}')
            print(f'📋 Response headers: {dict(response.headers)}')
            
            event_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    event_count += 1
                    current_time = time.strftime('%H:%M:%S')
                    print(f'[{current_time}] SSE Event {event_count}: {line}')
                    sse_events.put((current_time, line))
                    
                    # Check if connection is still active
                    if not connection_active:
                        print('🔌 Connection marked as inactive, stopping SSE monitor')
                        break
                        
        except Exception as e:
            print(f'❌ SSE connection error: {e}')
            import traceback
            traceback.print_exc()
        finally:
            print('🔌 SSE connection closed')
    
    # Start SSE monitor
    sse_thread = threading.Thread(target=sse_monitor)
    sse_thread.daemon = True
    sse_thread.start()
    
    # Wait for connection
    time.sleep(2)
    
    if not session_id:
        print('❌ Failed to establish SSE connection')
        return
    
    print(f'\n📤 Step 1: Sending tools/call request...')
    
    # Send tools/call request (this is what causes the issue)
    tools_call_request = {
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'tools/call',
        'params': {
            'name': 'listInvoices',
            'arguments': {}
        }
    }
    
    try:
        current_time = time.strftime('%H:%M:%S')
        print(f'📋 Sending POST request at {current_time}')
        start_time = time.time()
        
        response = requests.post('http://localhost:3000/mcp',
                               json=tools_call_request,
                               headers={'MCP-Session-Id': session_id},
                               timeout=10)
        
        end_time = time.time()
        print(f'📋 POST response received in {end_time - start_time:.3f}s')
        print(f'📋 POST status: {response.status_code}')
        print(f'📋 POST response: {response.text}')
        
        # Monitor SSE events for the next 5 seconds
        print(f'\n⏰ Monitoring SSE events for 5 seconds...')
        monitoring_start = time.time()
        
        events_received = 0
        while time.time() - monitoring_start < 5:
            try:
                timestamp, event = sse_events.get(timeout=0.1)
                events_received += 1
                # Events are already printed in the SSE monitor
            except Empty:
                continue
        
        connection_active = False
        print(f'\n📊 Analysis complete - received {events_received} events during monitoring')
        
    except Exception as e:
        print(f'❌ POST request failed: {e}')
        import traceback
        traceback.print_exc()
    
    # Give some time for final events
    time.sleep(2)

if __name__ == "__main__":
    deep_analyze_connection() 