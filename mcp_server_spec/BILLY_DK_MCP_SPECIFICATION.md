# Billy.dk MCP Server Specification

**Version**: 1.0.0  
**Protocol**: Model Context Protocol (MCP) 2024-11-05  
**Base URL**: `http://localhost:3000`  
**Transport**: HTTP with Server-Sent Events (SSE)

## Overview

The Billy.dk MCP Server provides access to Billy.dk accounting system functionality through the Model Context Protocol. It supports both modern MCP clients and Google ADK-specific integration patterns.

## Server Information

- **Name**: `billydk-mcp-server`
- **Version**: `1.0.0`
- **Protocol Version**: `2024-11-05`
- **Port**: `3000` (default)

## Transport Protocols

### 1. Modern MCP Client (HTTP/JSON-RPC)
**Endpoint**: `POST /mcp`  
**Usage**: Standard MCP clients using direct HTTP requests

### 2. ADK-Compatible SSE Protocol
**Endpoints**: 
- `POST /sse` (initialization)
- `GET /mcp` (SSE stream connection)  
- `POST /messages` (tool calls)

## Authentication & Session Management

### Session Creation
All interactions require a valid session. Sessions are created during the initialization process.

**Session ID Format**: UUID v4 (e.g., `550e8400-e29b-41d4-a716-446655440000`)  
**Session Header**: `MCP-Session-Id`  
**Session Lifetime**: Active until connection closed or server restart

## Endpoints Reference

### 1. Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "server": "billydk-mcp-server", 
  "version": "1.0.0",
  "timestamp": "2024-07-09T12:00:00.000Z",
  "connections": 2
}
```

### 2. Server Information
```http
GET /
```

**Response**: Complete server information including available endpoints and tools.

### 3. Modern MCP Client Endpoint
```http
POST /mcp
Content-Type: application/json
```

**Initialization Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "your-client-name",
      "version": "1.0.0"
    }
  }
}
```

**Tools List Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Tool Call Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "listInvoices",
    "arguments": {}
  }
}
```

### 4. ADK-Compatible Endpoints

#### 4.1 Session Initialization
```http
POST /sse
Content-Type: application/json
Accept: application/json, text/event-stream
```

**Request Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "google-adk-client",
      "version": "1.0.0"
    }
  }
}
```

**Response Headers**:
```
MCP-Session-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

**Response Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "listChanged": true },
      "prompts": { "listChanged": true }
    },
    "serverInfo": {
      "name": "billydk-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

#### 4.2 SSE Stream Connection
```http
GET /mcp
Accept: text/event-stream
MCP-Session-Id: {session-id}
```

**Response Headers**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Stream Events**:
```
:connected

data: {"jsonrpc":"2.0","method":"connection","params":{"sessionId":"...","version":"2024-11-05"}}

:ping
```

#### 4.3 Tool Execution
```http
POST /messages
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Session-Id: {session-id}
```

**Request Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "listInvoices",
    "arguments": {}
  }
}
```

**Response** (HTTP):
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "status": "message_sent_via_sse",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Response** (SSE Stream):
```
data: {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Found 5 invoices:\n• Invoice abc123: 1000 DKK - paid\n• Invoice def456: 2500 DKK - draft"}]}}
```

## Available Tools

### 1. listInvoices
**Description**: Returns all invoices from Billy.dk  
**Parameters**: None

**Example Request**:
```json
{
  "name": "listInvoices",
  "arguments": {}
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 3 invoices:\n• Invoice abc123: 1000 DKK - paid\n• Invoice def456: 2500 DKK - draft\n• Invoice ghi789: 750 DKK - sent"
    }
  ]
}
```

### 2. getInvoice
**Description**: Get a single invoice by ID  
**Parameters**:
- `id` (string, required): Invoice ID

**Example Request**:
```json
{
  "name": "getInvoice", 
  "arguments": {
    "id": "abc123"
  }
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Invoice #abc123: 1000 DKK - Status: paid\nContact: customer-456\nEntry Date: 2024-01-15"
    }
  ]
}
```

### 3. createInvoice
**Description**: Create a new invoice in Billy.dk  
**Parameters**:
- `contactId` (string, optional): Customer contact ID
- `amount` (number, optional): Invoice amount  
- `state` (string, optional): Invoice state

**Example Request**:
```json
{
  "name": "createInvoice",
  "arguments": {
    "contactId": "customer-789",
    "amount": 1500,
    "state": "draft"
  }
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text", 
      "text": "✅ Invoice created successfully! Invoice #new123: 1500 DKK - Status: draft"
    }
  ]
}
```

### 4. updateInvoice
**Description**: Update an existing invoice  
**Parameters**:
- `id` (string, required): Invoice ID
- `contactId` (string, optional): Customer contact ID
- `amount` (number, optional): Invoice amount
- `state` (string, optional): Invoice state

**Example Request**:
```json
{
  "name": "updateInvoice",
  "arguments": {
    "id": "abc123",
    "amount": 1200,
    "state": "sent"
  }
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Invoice updated successfully! Invoice #abc123: 1200 DKK - Status: sent"
    }
  ]
}
```

### 5. deleteInvoice
**Description**: Delete an invoice  
**Parameters**:
- `id` (string, required): Invoice ID

**Example Request**:
```json
{
  "name": "deleteInvoice",
  "arguments": {
    "id": "abc123"
  }
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Invoice abc123 deleted successfully"
    }
  ]
}
```

### 6. listCustomers
**Description**: Returns all customers from Billy.dk  
**Parameters**: None

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 2 customers:\n• John Doe (customer-456)\n• Jane Smith (customer-789)"
    }
  ]
}
```

### 7. createCustomer  
**Description**: Create a new customer in Billy.dk  
**Parameters**:
- `name` (string, optional): Customer name
- `email` (string, optional): Customer email

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Customer created successfully! Customer: John Doe (ID: customer-999)"
    }
  ]
}
```

### 8. listProducts
**Description**: Returns all products from Billy.dk  
**Parameters**: None

**Example Response**:
```json
{
  "content": [
    {
      "type": "text", 
      "text": "Found 3 products:\n• Web Design: 5000 DKK\n• Consulting: 1500 DKK\n• Support: 500 DKK"
    }
  ]
}
```

### 9. createProduct
**Description**: Create a new product in Billy.dk  
**Parameters**:
- `name` (string, optional): Product name
- `price` (number, optional): Product price

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Product created successfully! Product: New Service - Price: 2000 DKK (ID: product-555)"
    }
  ]
}
```

### 10. totalInvoiceAmount
**Description**: Get total invoice amount for a specified period  
**Parameters**:
- `startDate` (string, required): Start date (YYYY-MM-DD)
- `endDate` (string, required): End date (YYYY-MM-DD)

**Example Request**:
```json
{
  "name": "totalInvoiceAmount",
  "arguments": {
    "startDate": "2024-01-01",
    "endDate": "2024-12-31"
  }
}
```

**Example Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Total invoice amount from 2024-01-01 to 2024-12-31: 15750 DKK (12 invoices)"
    }
  ]
}
```

## Error Handling

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "Session not found or expired. Please re-establish connection."
  }
}
```

### Common Error Codes
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: Session-related errors

### Session Errors
- **Session Not Found**: Session ID not found in active sessions
- **Session Expired**: Session connection closed or expired
- **Connection Required**: SSE connection required for ADK flow

## Integration Examples

### Modern MCP Client Integration

```javascript
import fetch from 'node-fetch';

class BillyMcpClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async initialize() {
    const response = await fetch(`${this.baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "my-client", version: "1.0.0" }
        }
      })
    });
    return await response.json();
  }

  async callTool(name, arguments = {}) {
    const response = await fetch(`${this.baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: { name, arguments }
      })
    });
    return await response.json();
  }
}
```

### ADK-Compatible Integration

```javascript
class BillyAdkClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async initialize() {
    // Step 1: Initialize session
    const response = await fetch(`${this.baseUrl}/sse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "adk-client", version: "1.0.0" }
        }
      })
    });

    this.sessionId = response.headers.get('mcp-session-id');
    return this.sessionId;
  }

  async callTool(name, arguments = {}) {
    // Step 2: Call tool via /messages endpoint
    const response = await fetch(`${this.baseUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'MCP-Session-Id': this.sessionId
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: { name, arguments }
      })
    });

    const responseText = await response.text();
    return this.parseSSEResponse(responseText);
  }

  parseSSEResponse(responseText) {
    const lines = responseText.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        return JSON.parse(line.substring(6));
      }
    }
    throw new Error('No valid JSON found in SSE response');
  }
}
```

## Response Format Specifications

### Content Structure
All tool responses follow this structure:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Human-readable description of the result"
    }
  ]
}
```

### Text Format Requirements
- **Human-readable**: Responses must be descriptive text, not raw JSON
- **Structured**: Use bullet points, line breaks for readability  
- **Informative**: Include relevant details (IDs, amounts, statuses)
- **Consistent**: Follow established patterns for similar operations

### Examples of Correct vs Incorrect Formats

**✅ Correct (Human-readable)**:
```json
{
  "type": "text",
  "text": "Found 3 invoices:\n• Invoice abc123: 1000 DKK - paid\n• Invoice def456: 2500 DKK - draft"
}
```

**❌ Incorrect (Raw JSON)**:
```json
{
  "type": "text", 
  "text": "[{\"id\":\"abc123\",\"amount\":1000,\"status\":\"paid\"}]"
}
```

## CORS Support

The server includes CORS headers for cross-origin requests:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Authorization, MCP-Session-Id, Last-Event-ID
```

## Rate Limiting & Timeouts

- **Session Timeout**: Sessions remain active while SSE connection is maintained
- **Keep-Alive**: SSE connections send ping every 30 seconds
- **Connection Cleanup**: Automatic cleanup on client disconnect

## Troubleshooting

### Common Issues

1. **"Session not found" errors**
   - Ensure session ID is included in MCP-Session-Id header
   - Verify SSE connection is established and maintained
   - Check that initialization was successful

2. **Tool calls failing**
   - Verify tool name spelling and case sensitivity
   - Check parameter format and required fields
   - Ensure session is properly initialized

3. **SSE connection issues**
   - Confirm Accept header includes "text/event-stream"
   - Verify session ID is passed correctly
   - Check network connectivity and firewall settings

### Debug Endpoints

- `GET /health` - Check server status
- `GET /` - View complete server configuration
- Server logs provide detailed request/response information

## Version History

**v1.0.0** (Current)
- Initial release with full MCP 2024-11-05 support
- ADK-compatible SSE implementation
- 10 Billy.dk integration tools
- Human-readable response format
- Session management
- CORS support

---

*This specification is compatible with MCP Protocol 2024-11-05 and Google ADK integration requirements.* 