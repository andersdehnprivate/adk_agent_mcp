# 🔧 MCP SSE Endpoint Fix Required

## Issue Identified
The `/mcp/sse` endpoint in your Billy.dk MCP server is **timing out** on GET requests, causing the ADK web interface to hang when starting a chat.

## Root Cause
- ✅ MCP server health endpoint (`/health`) works fine
- ❌ MCP SSE endpoint (`/mcp/sse`) hangs and doesn't respond to GET requests
- This causes ADK agent creation to timeout during MCP toolset initialization

## Required Fix

### 1. Check Your `/mcp/sse` Endpoint Implementation

Your endpoint should respond to GET requests immediately with proper SSE headers:

```javascript
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers immediately
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Send initial connection event
  res.write('data: {"jsonrpc":"2.0","method":"initialized","params":{}}\n\n');
  
  // Keep connection alive
  const keepAlive = setInterval(() => {
    res.write('data: {"jsonrpc":"2.0","method":"ping"}\n\n');
  }, 30000);
  
  // Handle client disconnect
  req.on('close', () => {
    clearInterval(keepAlive);
    res.end();
  });
});
```

### 2. Common Issues to Check

1. **Endpoint Not Responding**: The handler might be waiting for something that never happens
2. **Missing Headers**: SSE requires specific headers to be set immediately
3. **Blocking Operations**: The endpoint might be doing synchronous operations that block the response
4. **Event Loop Blocking**: Long-running operations blocking the Node.js event loop

### 3. Debug Your Current Implementation

Add logging to see what's happening:

```javascript
app.get('/mcp/sse', (req, res) => {
  console.log('SSE endpoint called');
  
  try {
    // Your existing SSE logic here
    console.log('SSE headers set');
    
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    console.log('SSE response started');
    res.write('data: {"jsonrpc":"2.0","method":"initialized"}\n\n');
    
  } catch (error) {
    console.error('SSE endpoint error:', error);
    res.status(500).json({ error: 'SSE endpoint failed' });
  }
});
```

### 4. Test Your Fix

After fixing, test with:

```bash
# Should respond immediately (not timeout)
curl -N -H "Accept: text/event-stream" http://localhost:3000/mcp/sse
```

## Temporary Workaround (Optional)

If you need to test ADK without MCP tools temporarily, you can modify the agent to skip MCP:

```javascript
// In agents/billy_agent/agent.py, temporarily disable MCP:
mcp_server_url = None  # This will skip MCP toolset creation
```

## Verification

Once fixed, the ADK web interface should:
1. ✅ Load the agent without hanging
2. ✅ Start chat sessions immediately  
3. ✅ Have access to MCP tools
4. ✅ Show "MCP toolset added" in the logs

## Next Steps

1. **Fix the `/mcp/sse` endpoint** in your Billy.dk MCP server
2. **Test the endpoint** with curl to ensure it responds immediately
3. **Restart your MCP server**
4. **Test the ADK web interface** - it should no longer hang

The ADK side is working correctly - the issue is entirely on the MCP server side with the SSE endpoint implementation. 