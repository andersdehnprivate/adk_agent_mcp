# MCP Server Quick Fix - JSON-RPC 2.0 Protocol Issue

## Problem Identified
Your MCP server is sending a custom connection message:
```json
{"type":"connection","sessionId":"...","version":"2024-11-05"}
```

But ADK expects **JSON-RPC 2.0** format messages with required fields: `jsonrpc`, `method`, `id`, `params`.

## Quick Fix

### Step 1: Locate Your `/mcp/sse` Endpoint
Find this code in your MCP server:

```javascript
app.get('/mcp/sse', (req, res) => {
  // ... SSE setup code ...
  
  // FIND THIS LINE (or similar):
  res.write(`data: ${JSON.stringify({
    type: 'connection',
    sessionId: sessionId,
    version: '2024-11-05'
  })}\n\n`);
  
  // ... rest of code ...
});
```

### Step 2: Replace the Connection Message

**Option A: Remove Connection Message (Recommended)**
```javascript
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Send only the connected comment
  res.write(':connected\n\n');
  
  // Keep connection alive - DON'T send the connection data message
  // The client will send initialize request via POST
});
```

**Option B: Format as JSON-RPC 2.0 (Alternative)**
```javascript
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Send connection comment
  res.write(':connected\n\n');
  
  // Send JSON-RPC 2.0 formatted connection notification
  res.write(`data: ${JSON.stringify({
    jsonrpc: '2.0',
    method: 'connection',
    params: {
      sessionId: sessionId,
      version: '2024-11-05'
    }
  })}\n\n`);
});
```

### Step 3: Test the Fix

After making the change, test with:
```bash
python diagnose_mcp_issue.py
```

Expected result: **No more JSON-RPC validation errors**

## Why This Works

- **Before**: Server sends `{"type":"connection",...}` → Missing `jsonrpc` field → ADK validation fails
- **After**: Server either sends no message or proper JSON-RPC 2.0 format → ADK validation passes

## Complete Working Example

Here's a complete working `/mcp/sse` endpoint:

```javascript
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers immediately
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Generate session ID
  const sessionId = generateSessionId();
  
  // Store connection for later use
  connections.set(sessionId, res);
  
  // Send connected event (no data message needed)
  res.write(':connected\n\n');
  
  // Keep connection alive
  const keepAlive = setInterval(() => {
    res.write(':ping\n\n');
  }, 30000);
  
  // Handle client disconnect
  req.on('close', () => {
    clearInterval(keepAlive);
    connections.delete(sessionId);
  });
});
```

## Expected Behavior After Fix

1. ✅ No more JSON-RPC validation errors
2. ✅ ADK can connect to MCP server
3. ✅ MCP tools will be available in ADK web interface
4. ✅ Billy.dk invoice management tools will work

## Files to Check

- Your MCP server's main file (likely `server.js` or `index.js`)
- Look for the `/mcp/sse` route handler
- Make sure the POST `/mcp` endpoint is also working (it seems to be based on diagnostics)

After implementing this fix, your MCP server will be compatible with ADK's JSON-RPC 2.0 expectations! 