# CRITICAL: Server Session Management Fix Required

## 🚨 **EXACT PROBLEM IDENTIFIED**

Your server logs show:
```
SSE connection established: e84fd52b-288c-402f-bcb3-278d2eb09d3d
```

But your POST responses show:
```json
{"status":"message_sent_via_sse","sessionId":"e84fd52b-288c-402f-bcb3-278d2eb09d3d"}
```

**The server is NOT actually sending responses via SSE!**

## 🔧 **CRITICAL FIX NEEDED**

Your server must implement this **exact session management**:

### **Step 1: Store SSE Connections**
```javascript
// At the top of your server file
const activeSessions = new Map();
```

### **Step 2: SSE Endpoint - Store Connection**
```javascript
app.get('/mcp/sse', (req, res) => {
  // Set headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  const sessionId = generateSessionId();
  
  // CRITICAL: Store this SSE connection
  activeSessions.set(sessionId, res);
  
  // Send session ID in header
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
    console.log(`Session ${sessionId} disconnected`);
  });
});
```

### **Step 3: POST Endpoint - Send Response via SSE**
```javascript
app.post('/mcp', (req, res) => {
  const sessionId = req.headers['mcp-session-id'];
  
  // CRITICAL: Find the stored SSE connection
  const sseConnection = activeSessions.get(sessionId);
  
  if (!sseConnection) {
    return res.status(400).json({
      jsonrpc: '2.0',
      error: { code: -32000, message: 'No active SSE connection found' }
    });
  }
  
  const { jsonrpc, method, params, id } = req.body;
  
  let response;
  
  if (method === 'initialize') {
    // CRITICAL: Create actual response
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
          {
            name: 'get_invoices',
            description: 'Get invoices from Billy.dk',
            inputSchema: {
              type: 'object',
              properties: {
                limit: { type: 'number' }
              }
            }
          }
          // Add more Billy.dk tools
        ]
      }
    };
  } else {
    response = {
      jsonrpc: '2.0',
      id: id,
      error: { code: -32601, message: `Method not found: ${method}` }
    };
  }
  
  // CRITICAL: Send response via SSE (THIS IS THE KEY!)
  try {
    sseConnection.write(`data: ${JSON.stringify(response)}\n\n`);
    console.log(`✅ Response sent via SSE for session: ${sessionId}`);
    
    // Return simple acknowledgment to POST
    res.status(200).json({
      jsonrpc: '2.0',
      result: { status: 'sent' }
    });
  } catch (error) {
    console.error('Failed to send via SSE:', error);
    res.status(500).json({
      jsonrpc: '2.0',
      error: { code: -32000, message: 'Failed to send response' }
    });
  }
});
```

## 🧪 **How to Test the Fix**

After implementing this fix, you should see:

**Server logs:**
```
SSE connection established: [session-id]
✅ Response sent via SSE for session: [session-id]
```

**POST response:**
```json
{"jsonrpc":"2.0","result":{"status":"sent"}}
```

**SSE connection receives:**
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

## 🎯 **Current Issue**

Your server currently:
- ✅ Establishes SSE connections
- ✅ Receives POST requests  
- ❌ **Says "message_sent_via_sse" but doesn't actually send it**
- ❌ **Missing: activeSessions.set() and sseConnection.write()**

## ✅ **Success Criteria**

After the fix:
- Chat stops spinning immediately
- ADK receives actual initialization responses
- MCP tools become accessible
- Billy.dk functionality works through chat

**The server is 95% there - it just needs the actual session management implementation!** 