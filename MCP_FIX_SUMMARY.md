# MCP Server Fix - Critical Race Condition

## 🐛 **Issue**
ADK times out when getting tools due to race condition in server's `/mcp/sse` endpoint.

**Problem**: Server sends `MCP-Session-Id` header before storing the SSE connection, so ADK gets "No active SSE connection found" error.

## 🔧 **Fix Required**
In your server's `/mcp/sse` endpoint, change the order:

```javascript
// ❌ BROKEN ORDER:
res.setHeader('MCP-Session-Id', sessionId);  // Send header first
activeSessions.set(sessionId, res);          // Store connection second

// ✅ CORRECT ORDER:
activeSessions.set(sessionId, res);          // Store connection FIRST
res.setHeader('MCP-Session-Id', sessionId);  // Send header SECOND
```

## 🧪 **Test**
After fix, run: `python test_adk_mcp_flow.py`

Expected result: `✅ Tools retrieved: 10 tools found`

## 📊 **Status**
- ✅ Server session management working
- ✅ Tools endpoint working  
- ✅ JSON-RPC protocol working
- ❌ Race condition causing ADK timeout

**Fix this one timing issue and MCP integration is 100% complete!** 