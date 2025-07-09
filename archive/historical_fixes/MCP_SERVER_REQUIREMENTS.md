# 🔧 MCP Server Implementation Requirements for ADK Compatibility

This document outlines the exact requirements for implementing an MCP server that works with Google ADK (Agent Development Kit).

## 📊 Current Server Status Analysis

Based on diagnostics of the Billy.dk MCP server, the current implementation has:

- ✅ `/mcp` - Main endpoint (SSE stream, times out waiting for connections)
- ✅ `/health` - Health check endpoint  
- ✅ `/messages` - Message handling endpoint
- ❌ `/mcp/sse` - **MISSING** - This is what ADK expects

## 🎯 Required Implementation

### 1. Add `/mcp/sse` Endpoint

ADK expects this specific endpoint for SSE connections:

```javascript
// Add this endpoint to your MCP server
app.get('/mcp/sse', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Handle SSE connection for MCP protocol
  // This should implement the MCP SSE protocol as per spec
});
```

### 2. SSE Protocol Implementation

The `/mcp/sse` endpoint must support:

**Request Flow:**
1. **GET** `/mcp/sse` - Initial SSE connection
2. **POST** `/mcp/sse` - Send JSON-RPC 2.0 messages
3. **SSE Events** - Receive responses as Server-Sent Events

**Required Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
```

### 3. Message Flow Implementation

Your `/mcp/sse` endpoint needs to handle:

```javascript
// Example implementation structure
app.get('/mcp/sse', (req, res) => {
  // Initialize SSE connection
  const sessionId = req.headers['mcp-session-id'] || generateSessionId();
  
  // Send initial connection event
  res.write(`data: ${JSON.stringify({
    type: 'connection',
    sessionId: sessionId
  })}\n\n`);
  
  // Handle MCP protocol messages
  // - Initialize requests
  // - Tools list requests  
  // - Tool invocation requests
});

app.post('/mcp/sse', (req, res) => {
  // Handle JSON-RPC 2.0 messages
  const { method, params, id } = req.body;
  
  // Process MCP methods:
  // - initialize
  // - tools/list
  // - tools/call
  // - etc.
});
```

### 4. URL Structure Expected by ADK

```
Base URL: MCP_SERVER_URL=http://localhost:3000
ADK automatically appends: /sse
Final URL: http://localhost:3000/sse

OR

Base URL: MCP_SERVER_URL=http://localhost:3000/mcp  
ADK automatically appends: /sse
Final URL: http://localhost:3000/mcp/sse ← This is what you need
```

### 5. Protocol Compatibility

Ensure your server supports:
- **MCP Protocol Version**: `2024-11-05`
- **Transport**: `streamable-http` (SSE-based)
- **JSON-RPC 2.0** message format
- **Required Methods**: `initialize`, `tools/list`, `tools/call`

## 💡 Implementation Options

### Option A: Add `/mcp/sse` Endpoint (Recommended)

```javascript
// Add to your existing server
app.get('/mcp/sse', handleSSEConnection);
app.post('/mcp/sse', handleSSEMessages);
```

### Option B: Modify URL Structure

Change your server to serve the main SSE endpoint at `/sse` and set:
```
MCP_SERVER_URL=http://localhost:3000
```

### Option C: Add Route Alias

```javascript
// Make /mcp/sse point to your existing /mcp endpoint
app.get('/mcp/sse', (req, res) => {
  // Forward to your existing /mcp handler
  handleMCPConnection(req, res);
});
```

## 🧪 Testing Your Implementation

Once implemented, test with:

```bash
# Test SSE connection
curl -N -H "Accept: text/event-stream" http://localhost:3000/mcp/sse

# Test POST messages
curl -X POST http://localhost:3000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05"},"id":1}'
```

## 📋 Quick Fix

The fastest solution is to add this to your server:

```javascript
app.all('/mcp/sse', (req, res) => {
  // Forward all requests to your existing /mcp handler
  req.url = '/mcp';
  yourExistingMCPHandler(req, res);
});
```

## 🔄 Current Error Analysis

The recurring 404 errors occur because:

1. **ADK Configuration**: `MCP_SERVER_URL=http://localhost:3000/mcp`
2. **ADK Expectation**: Automatically appends `/sse` → `http://localhost:3000/mcp/sse`
3. **Server Reality**: Only `/mcp` exists, not `/mcp/sse`
4. **Result**: HTTP 404 Not Found

## ✅ Success Criteria

Once you implement the `/mcp/sse` endpoint:

1. ✅ ADK will connect successfully
2. ✅ No more 404 errors
3. ✅ MCP tools will be accessible through the web interface
4. ✅ Invoice management functionality will work

## 🔗 Related Files

- `agents/mcp_agent/agent.py` - ADK agent configuration
- `.env` - Environment variables including `MCP_SERVER_URL`
- MCP server codebase - Where `/mcp/sse` endpoint needs to be added

## 📚 Additional Resources

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [ADK Documentation](https://developers.google.com/adk)
- [Server-Sent Events (SSE) Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

**Once you implement the `/mcp/sse` endpoint, the 404 errors will disappear and ADK will be able to connect to your MCP server properly.** 