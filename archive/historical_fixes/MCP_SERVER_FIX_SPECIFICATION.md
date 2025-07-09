# Billy.dk MCP Server Fix Specification

## 🎯 **Objective**
Fix the Billy.dk MCP server to properly implement the MCP (Model Context Protocol) so it works with ADK (Agent Development Kit).

## 🔍 **Current Issues Identified**

### ✅ **What's Working:**
- MCP server starts successfully on `http://localhost:3000`
- Health endpoint: `GET /health` → `200 OK`
- SSE endpoint connects: `GET /mcp/sse` → `200 OK` with proper headers
- Initial connection event: `:connected`

### ❌ **What's Broken:**
1. **SSE Protocol**: Only sends `:connected`, then stops - no JSON-RPC 2.0 messages
2. **POST Endpoint**: Returns 406 "Not Acceptable" for initialization requests
3. **Tool Discovery**: No mechanism to list available Billy.dk tools
4. **Message Handling**: No response to MCP protocol messages

## 📋 **Required Fixes**

### **Fix 1: SSE Endpoint Protocol Implementation**

**Current Behavior:**
```
GET /mcp/sse
→ 200 OK
→ :connected
→ [connection hangs indefinitely]
```

**Required Behavior:**
```
GET /mcp/sse
→ 200 OK
→ :connected

[Wait for POST initialization, then send via SSE:]
→ data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"serverInfo":{"name":"billydk-mcp-server","version":"1.0.0"}}}

→ data: {"jsonrpc":"2.0","method":"notifications/tools/list_changed","params":{}}

[Keep connection alive for real-time updates]
```

**Implementation Requirements:**
- Keep SSE connection alive indefinitely
- Send JSON-RPC 2.0 messages as `data: {json}` events
- Respond to initialization with server capabilities
- Send tool list notifications
- Handle incoming messages from POST endpoint

### **Fix 2: POST Endpoint Header Handling**

**Current Behavior:**
```
POST /mcp
Content-Type: application/json
→ 406 Not Acceptable: Client must accept both application/json and text/event-stream
```

**Required Behavior:**
```
POST /mcp
Content-Type: application/json
→ 200 OK (process the JSON-RPC request)
```

**Implementation Requirements:**
- Accept `Content-Type: application/json` 
- Process JSON-RPC 2.0 requests
- Handle initialization method
- Handle tool invocation methods
- Send responses back via SSE connection

### **Fix 3: MCP Protocol Message Handling**

**Required Messages to Handle:**

#### **Initialize Request**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {"listChanged": true},
      "sampling": {}
    },
    "clientInfo": {
      "name": "ADK",
      "version": "1.0.0"
    }
  }
}
```

**Response (via SSE):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"listChanged": true},
      "prompts": {"listChanged": true}
    },
    "serverInfo": {
      "name": "billydk-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

#### **Tools List Request**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response (via SSE):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_invoices",
        "description": "Get invoices from Billy.dk",
        "inputSchema": {
          "type": "object",
          "properties": {
            "status": {"type": "string", "enum": ["draft", "sent", "paid", "overdue"]},
            "limit": {"type": "integer", "default": 10}
          }
        }
      },
      {
        "name": "create_invoice",
        "description": "Create a new invoice in Billy.dk",
        "inputSchema": {
          "type": "object",
          "properties": {
            "customer_id": {"type": "string", "required": true},
            "items": {"type": "array", "required": true}
          }
        }
      },
      {
        "name": "get_customers",
        "description": "Get customers from Billy.dk",
        "inputSchema": {
          "type": "object",
          "properties": {
            "limit": {"type": "integer", "default": 10}
          }
        }
      }
    ]
  }
}
```

#### **Tool Call Request**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_invoices",
    "arguments": {
      "status": "sent",
      "limit": 5
    }
  }
}
```

**Response (via SSE):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 5 sent invoices:\n1. Invoice #1001 - $150.00 - Customer ABC\n2. Invoice #1002 - $250.00 - Customer XYZ\n..."
      }
    ]
  }
}
```

### **Fix 4: Connection Management**

**Requirements:**
- Maintain mapping between SSE connections and sessions
- Route POST requests to correct SSE connection
- Handle connection cleanup on disconnect
- Support multiple concurrent ADK connections

**Example Session Management:**
```javascript
// Pseudo-code structure
const sessions = new Map(); // sessionId -> sseConnection

// On SSE connect
app.get('/mcp/sse', (req, res) => {
  const sessionId = generateSessionId();
  sessions.set(sessionId, res);
  res.write(':connected\n\n');
  // Keep connection alive
});

// On POST request
app.post('/mcp', (req, res) => {
  const sessionId = req.headers['mcp-session-id'] || getDefaultSession();
  const sseConnection = sessions.get(sessionId);
  
  // Process JSON-RPC request
  const response = processJsonRpcRequest(req.body);
  
  // Send response via SSE
  sseConnection.write(`data: ${JSON.stringify(response)}\n\n`);
  
  // Return 200 OK for POST
  res.status(200).json({"status": "sent"});
});
```

## 🧪 **Testing Requirements**

### **Test 1: SSE Connection Test**
```bash
# Should connect and receive :connected event
curl -N -H "Accept: text/event-stream" http://localhost:3000/mcp/sse
```

### **Test 2: Initialization Test**
```bash
# Should return 200 OK and send response via SSE
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

### **Test 3: Tool List Test**
```bash
# Should return available Billy.dk tools
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

### **Test 4: Tool Call Test**
```bash
# Should execute tool and return results
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_invoices","arguments":{"limit":5}}}'
```

### **Test 5: ADK Integration Test**
```bash
# Run our diagnostic tool
python diagnose_mcp_issue.py
```

**Expected Results:**
- ✅ SSE connection established
- ✅ Multiple JSON-RPC events received
- ✅ POST requests return 200 OK
- ✅ Tool discovery works
- ✅ ADK agent creation succeeds

## 📁 **Billy.dk Tool Implementation**

### **Required Tools:**

1. **get_invoices** - List invoices with filtering
2. **create_invoice** - Create new invoice
3. **get_customers** - List customers
4. **update_invoice** - Update existing invoice
5. **get_invoice_details** - Get specific invoice details
6. **send_invoice** - Send invoice to customer

### **Billy.dk API Integration:**
- Use existing Billy.dk API credentials
- Handle authentication properly
- Return formatted results suitable for AI processing
- Include error handling for API failures

## 🚀 **Implementation Priority**

1. **High Priority**: Fix SSE protocol implementation (Fix 1)
2. **High Priority**: Fix POST endpoint headers (Fix 2)  
3. **Medium Priority**: Implement basic tool discovery (Fix 3)
4. **Medium Priority**: Add connection management (Fix 4)
5. **Low Priority**: Implement all Billy.dk tools

## ✅ **Success Criteria**

The fix is complete when:
- [ ] ADK can connect to MCP server without hanging
- [ ] ADK can see available Billy.dk tools
- [ ] ADK can invoke tools and get results
- [ ] Multiple ADK sessions can connect simultaneously
- [ ] MCP server handles errors gracefully

## 📞 **Testing Command**

Once fixes are implemented, test with:
```bash
cd "C:\Users\AndersDehn\CascadeProjects\adk project"
python diagnose_mcp_issue.py
```

This should show:
```
✅ Multiple events received
✅ POST requests successful
✅ Tool discovery working
```

Then test ADK integration:
```bash
adk web
# Navigate to http://localhost:8000
# Select "billy_invoice_agent"
# Start chat (should not hang)
```

---

**This specification provides everything needed to fix the Billy.dk MCP server for ADK compatibility.** 