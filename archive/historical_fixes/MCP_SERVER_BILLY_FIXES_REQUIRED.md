# MCP Server Billy.dk Integration Fixes Required

## Problem
Billy.dk MCP server returns raw JSON data instead of human-readable text, violating MCP protocol and causing ADK chat to spin endlessly.

## Current Behavior (BROKEN)
```json
{
  "type": "text", 
  "text": "[{\"id\": \"zIG8...\", \"amount\": 1000, \"status\": \"paid\"}]"
}
```

## Required Behavior (CORRECT)
```json
{
  "type": "text",
  "text": "Found 1 invoice: Invoice #zIG8... for $1,000.00 (Status: paid)"
}
```

## Required Changes

### 1. Tool Response Formatting
- **Location**: All tool response handlers in MCP server
- **Change**: Convert JSON data to descriptive text before returning
- **Rule**: The `text` field must contain human-readable descriptions, not raw JSON

### 2. Invoice Tool Example
```javascript
// BEFORE (broken)
return { type: "text", text: JSON.stringify(invoices) };

// AFTER (correct)
return { 
  type: "text", 
  text: `Found ${invoices.length} invoice(s): ${invoices.map(inv => 
    `Invoice #${inv.id} for $${inv.amount} (Status: ${inv.status})`
  ).join(', ')}`
};
```

### 3. General Pattern
- Parse/process the data internally
- Format as natural language descriptions  
- Return descriptive text that an LLM can understand and use
- Never return raw JSON arrays or objects in the text field

## Impact
This fix will resolve the ADK chat spinning issue and ensure proper MCP protocol compliance. 