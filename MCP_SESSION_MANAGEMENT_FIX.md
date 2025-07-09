# MCP Session Management Fix

## Problem Identified
- ✅ Server receives POST `/mcp` requests correctly
- ✅ Server establishes SSE `/mcp/sse` connections correctly  
- ❌ **Server is NOT sending POST responses back via SSE**

This causes ADK to hang waiting for responses that never arrive.

## Root Cause
The POST endpoint and SSE endpoint are not properly linked. When a POST request comes in, the server needs to:
1. Process the JSON-RPC request
2. Find the corresponding SSE connection
3. Send the response back via that SSE connection

## Required Fix

### Step 1: Session Management
Your server needs to maintain a mapping between sessions and SSE connections:

```javascript
// Store active SSE connections
const activeSessions = new Map();

// SSE endpoint - store connection
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Generate session ID
  const sessionId = generateSessionId();
  
  // Store this connection
  activeSessions.set(sessionId, res);
  
  // Send session ID back to client
  res.setHeader('MCP-Session-Id', sessionId);
  
  // Send initial events
  res.write(':connected\n\n');
  res.write(`data: ${JSON.stringify({
    jsonrpc: '2.0',
    method: 'connection',
    params: { sessionId, version: '2024-11-05' }
  })}\n\n`);
  
  // Clean up on disconnect
  req.on('close', () => {
    activeSessions.delete(sessionId);
  });
});
```

### Step 2: POST Response Handling
Your POST endpoint needs to send responses back via SSE:

```javascript
app.post('/mcp', (req, res) => {
  const sessionId = req.headers['mcp-session-id'];
  const sseConnection = activeSessions.get(sessionId);
  
  if (!sseConnection) {
    return res.status(400).json({
      error: 'No active SSE connection found'
    });
  }
  
  // Process the JSON-RPC request
  const { jsonrpc, method, params, id } = req.body;
  
  let response;
  
  if (method === 'initialize') {
    response = {
      jsonrpc: '2.0',
      id: id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: { listChanged: true },
          resources: { listChanged: true },
          prompts: { listChanged: true }
        },
        serverInfo: {
          name: 'billydk-mcp-server',
          version: '1.0.0'
        }
      }
    };
  } else if (method === 'tools/list') {
    response = {
      jsonrpc: '2.0',
      id: id,
      result: {
        tools: [
          // Your Billy.dk tools here
          {
            name: 'get_invoices',
            description: 'Get list of invoices',
            inputSchema: {
              type: 'object',
              properties: {
                limit: { type: 'number', description: 'Max number of invoices' }
              }
            }
          }
          // Add more tools...
        ]
      }
    };
  } else {
    response = {
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32601,
        message: `Method not found: ${method}`
      }
    };
  }
  
  // Send response back via SSE
  sseConnection.write(`data: ${JSON.stringify(response)}\n\n`);
  
  // Return 200 OK to POST request
  res.status(200).json({ status: 'sent' });
});
```

### Step 3: Session ID Header
Make sure ADK can send the session ID back:

```javascript
// In your SSE endpoint, make sure to set the session ID header
res.setHeader('MCP-Session-Id', sessionId);
```

## Testing the Fix

After implementing this fix, test with:

```bash
# Test that initialization works
python test_mcp_protocol.py
```

You should see:
1. ✅ SSE connection established
2. ✅ POST request sent
3. ✅ **Response received via SSE**
4. ✅ Chat stops "thinking" and works

## Common Issues to Check

1. **Session ID mismatch**: Make sure the session ID from SSE is used in POST requests
2. **Connection cleanup**: Clean up sessions when SSE connections close
3. **Error handling**: Handle cases where SSE connection is lost
4. **Response format**: Ensure all responses are valid JSON-RPC 2.0

## Expected Behavior After Fix

1. User starts chat in ADK
2. ADK connects to `/mcp/sse` → gets session ID
3. ADK sends POST to `/mcp` with session ID
4. Server processes request and sends response via SSE
5. ADK receives response and chat works normally

Your server logs should show:
```
POST /mcp REQUEST: initialize
Sending response via SSE to session: [session-id]
Response sent successfully
```

Instead of just hanging after the POST request. 