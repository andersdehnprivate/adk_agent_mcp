# MCP Protocol Issue Fix

## Problem
Your MCP server is sending a custom "connection" message:
```json
{"type": "connection", "sessionId": "...", "version": "2024-11-05"}
```

But ADK expects proper JSON-RPC 2.0 messages with required fields:
- `jsonrpc`: "2.0"
- `method`: The method name
- `id`: Request ID
- `params`: Parameters (optional)

## Solution
Your MCP server's `/mcp/sse` endpoint needs to send JSON-RPC 2.0 formatted messages.

### What ADK Expects
1. **Initial connection**: The SSE stream should start without sending a "connection" message
2. **Method calls**: All messages should be JSON-RPC 2.0 format
3. **Responses**: All responses should be JSON-RPC 2.0 format

### Example Fix for Your Server
Instead of sending:
```json
{"type": "connection", "sessionId": "1234", "version": "2024-11-05"}
```

Your server should either:
1. **Don't send an initial message** (preferred)
2. **Or send a proper JSON-RPC notification**:
```json
{
  "jsonrpc": "2.0",
  "method": "connection",
  "params": {
    "sessionId": "1234",
    "version": "2024-11-05"
  }
}
```

### Quick Fix
Update your `/mcp/sse` endpoint to:
1. Remove the initial "connection" message
2. Wait for the client to send the `initialize` method
3. Respond with proper JSON-RPC 2.0 format

### Example Initialize Response
When client sends:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {...},
    "clientInfo": {...}
  }
}
```

Server should respond:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {...},
    "serverInfo": {
      "name": "billydk-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

## Testing
After fixing, test with:
```bash
python test_mcp_simple.py
```

The connection should work without JSON-RPC validation errors. 