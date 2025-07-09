# Billy.dk MCP Server API Fix

## 🚨 **Issue**: Billy.dk API Field Mapping Error

**Error**: `Unknown attribute 'totalAmount' for 'invoice' record`

**Root Cause**: MCP server is sending incorrect field names to Billy.dk API.

## 🔧 **Fix Required**

### 1. **Update createInvoice Tool Schema**
```javascript
// WRONG (current):
{
  "contactId": "string",
  "totalAmount": "number",  // ❌ Billy.dk doesn't recognize this field
  "state": "string"
}

// CORRECT (needs investigation):
{
  "contactId": "string",
  "amount": "number",       // ✅ Or whatever Billy.dk expects
  "state": "string"
}
```

### 2. **Check Billy.dk API Documentation**
- Look up the correct field names for invoice creation
- Common alternatives: `amount`, `total`, `price`, or `lineItems`

### 3. **Update MCP Server Code**
- Fix the field mapping in your `createInvoice` tool implementation
- Update the tool's `inputSchema` to match Billy.dk's expected fields

## 🧪 **Test the Fix**
```bash
# Test after fixing field names
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"createInvoice","arguments":{"contactId":"test","amount":100,"state":"draft"}},"id":1}'
```

## ✅ **Expected Result**
- ✅ No more 400/422 errors
- ✅ Invoice created successfully in Billy.dk
- ✅ ADK agent can create invoices via chat

**Status**: MCP integration is working perfectly - just needs correct Billy.dk field names. 