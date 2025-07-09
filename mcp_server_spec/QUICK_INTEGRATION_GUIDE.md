# Billy.dk MCP Server - Quick Integration Guide

## Essential Information

**Base URL**: `http://localhost:3000`  
**Protocol**: MCP 2024-11-05  
**Session Header**: `MCP-Session-Id`

## Quick Start: Modern MCP Client

```javascript
// 1. Initialize
const init = await fetch('http://localhost:3000/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: "2.0", id: 1, method: "initialize",
    params: {
      protocolVersion: "2024-11-05", capabilities: {},
      clientInfo: { name: "my-client", version: "1.0.0" }
    }
  })
});

// 2. Call Tool
const result = await fetch('http://localhost:3000/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: "2.0", id: 2, method: "tools/call",
    params: { name: "listInvoices", arguments: {} }
  })
});
```

## Quick Start: ADK-Compatible Client

```javascript
// 1. Initialize Session
const init = await fetch('http://localhost:3000/sse', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
  },
  body: JSON.stringify({
    jsonrpc: "2.0", id: 1, method: "initialize",
    params: { protocolVersion: "2024-11-05", capabilities: {}, 
              clientInfo: { name: "adk-client", version: "1.0.0" }}
  })
});

const sessionId = init.headers.get('mcp-session-id');

// 2. Call Tool
const result = await fetch('http://localhost:3000/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream',
    'MCP-Session-Id': sessionId
  },
  body: JSON.stringify({
    jsonrpc: "2.0", id: 2, method: "tools/call",
    params: { name: "listInvoices", arguments: {} }
  })
});
```

## Available Tools (10 total)

| Tool | Parameters | Purpose |
|------|------------|---------|
| `listInvoices` | none | Get all invoices |
| `getInvoice` | `id` (required) | Get specific invoice |
| `createInvoice` | `contactId`, `amount`, `state` | Create invoice |
| `updateInvoice` | `id` (req), `contactId`, `amount`, `state` | Update invoice |
| `deleteInvoice` | `id` (required) | Delete invoice |
| `listCustomers` | none | Get all customers |
| `createCustomer` | `name`, `email` | Create customer |
| `listProducts` | none | Get all products |
| `createProduct` | `name`, `price` | Create product |
| `totalInvoiceAmount` | `startDate` (req), `endDate` (req) | Get total for period |

## Response Format

All tools return human-readable text:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 3 invoices:\n• Invoice abc123: 1000 DKK - paid\n• Invoice def456: 2500 DKK - draft"
    }
  ]
}
```

## Key Endpoints

- `GET /health` - Server status
- `GET /` - Server info  
- `POST /mcp` - Modern MCP client
- `POST /sse` - ADK session init
- `GET /mcp` - ADK SSE stream  
- `POST /messages` - ADK tool calls

## Common Errors

- `-32000`: Session issues (check session ID)
- `-32601`: Method not found (check tool name)  
- `-32603`: Internal error (check parameters)

## Testing Commands

```bash
# Health check
curl http://localhost:3000/health

# Modern client tool call
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"listInvoices","arguments":{}}}'
```

## Development Notes

- Always include `jsonrpc: "2.0"` in requests
- Use unique IDs for each request
- Check response format is human-readable text (not raw JSON)
- For ADK: maintain session ID across requests
- Server logs provide detailed debugging information

---

See `BILLY_DK_MCP_SPECIFICATION.md` for complete documentation. 