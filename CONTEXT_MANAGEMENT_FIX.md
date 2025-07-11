# Context Management Fix

## Problem Description

The ADK agent was experiencing context management issues where it would confuse different types of data during conversations. For example:

1. User shows a list of customers
2. User asks "show me the 3 latest created"
3. Agent incorrectly shows invoices instead of customers

## Root Cause Analysis

The issue was caused by:

1. **Insufficient context awareness** in the agent instructions
2. **Ambiguous tool descriptions** that didn't clearly differentiate between customer and invoice operations
3. **Lack of explicit conversation context rules** to guide the LLM's decision-making

## Solution Implemented

### 1. Enhanced Agent Instructions

Added explicit context awareness rules to the agent's instruction:

```python
CRITICAL: Always maintain conversation context and understand what data type you're working with.

Context Awareness Rules:
1. If the user just showed/discussed CUSTOMERS, follow-up questions about "latest", "recent", "show me X" refer to CUSTOMERS
2. If the user just showed/discussed INVOICES, follow-up questions about "latest", "recent", "show me X" refer to INVOICES  
3. If unclear, ask for clarification: "Do you mean customers or invoices?"
4. Pay attention to the current conversation topic - don't switch between customers and invoices randomly
```

### 2. Improved Tool Descriptions

Enhanced function docstrings to be more specific:

```python
async def list_customers() -> str:
    """List all customers from Billy.dk. Use this when user asks about customers, not invoices."""

async def list_invoices() -> str:
    """List all invoices from Billy.dk. Use this when user asks about invoices, not customers."""
```

### 3. Context Preservation Guidelines

Added specific instructions for maintaining conversation context:

- "MAINTAIN CONVERSATION CONTEXT - remember what data type we're discussing"
- "If asked for 'latest X' or 'recent X', understand this refers to the current topic of conversation"
- "Keep responses concise and focused, but always stay contextually aware"

## Testing

Created comprehensive tests to verify the fix:

### Test Scenarios

1. **Customer Context Test**:
   - User shows customers → asks for "latest 3" → should call `list_customers()`

2. **Invoice Context Test**:
   - User shows invoices → asks for "latest 3" → should call `list_invoices()`

3. **Ambiguous Context Test**:
   - User asks for "latest 3" without context → should ask for clarification

## Files Modified

1. `billy_agent/agent.py` - Enhanced agent instructions, tool descriptions, and **dynamic tool discovery**
2. `CONTEXT_MANAGEMENT_FIX.md` - This documentation

## Additional Enhancement: Dynamic Tool Discovery

After fixing the context management issue, we also implemented **dynamic tool discovery** to automatically find all available tools from the MCP server:

- **Before**: Agent used 5 hardcoded tools
- **After**: Agent dynamically discovers all 11 tools from MCP server
- **Benefits**: 
  - No maintenance needed when MCP server tools change
  - Automatic access to new tools added to MCP server
  - Tool descriptions pulled directly from MCP server metadata

## MCP Session Management Fix

We also fixed a critical issue where the agent couldn't access data from the MCP server:

### The Problem
- Agent could discover tools but couldn't access data when tools were called
- Event loop and session management issues causing "no access to data" errors
- Global MCP client sessions getting closed between requests

### The Solution
1. **Fresh Sessions**: Each MCP request now uses a fresh `aiohttp.ClientSession`
2. **No Global Sessions**: Removed shared session management to avoid event loop conflicts
3. **Simplified Client**: Streamlined MCP client to avoid session reuse issues

### Results
- ✅ **Data Access Working**: Agent can now retrieve 46 customers and 91 invoices
- ✅ **No Session Errors**: Fresh sessions prevent event loop conflicts
- ✅ **Reliable Operation**: Consistent data access across all tool calls

## How to Test

1. Start the ADK web interface:
   ```bash
   adk web
   ```

2. Test the conversation flow:
   - Show customers list
   - Ask for "latest 3 created"
   - Agent should correctly understand you mean customers

## Expected Behavior

The agent will now:
- ✅ Maintain conversation context between messages
- ✅ Understand when follow-up questions refer to the current topic
- ✅ Ask for clarification when context is ambiguous
- ✅ Use the correct tools based on conversation context
- ❌ No longer confuse customers with invoices

## Benefits

1. **Improved User Experience**: More natural conversation flow
2. **Reduced Errors**: Fewer instances of wrong tool usage
3. **Better Context Awareness**: Agent remembers what's being discussed
4. **Clearer Communication**: Agent asks for clarification when needed

This fix ensures the ADK agent maintains proper conversation context and provides accurate, contextually-aware responses. 