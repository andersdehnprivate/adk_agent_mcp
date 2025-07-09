/**
 * ADK Integration Example - Current SSE Protocol
 * This shows exactly how to integrate with the MCP server using SSE
 */

import fetch from 'node-fetch';

class McpSseClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  /**
   * Step 1: Initialize session with SSE
   */
  async initialize() {
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
          clientInfo: {
            name: "google-adk-client",
            version: "1.0.0"
          }
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Initialization failed: ${response.status}`);
    }

    // Extract session ID from response headers
    this.sessionId = response.headers.get('mcp-session-id');
    if (!this.sessionId) {
      throw new Error('No session ID received');
    }

    console.log('✅ Session initialized:', this.sessionId);
    return this.sessionId;
  }

  /**
   * Step 2: Call tools via /messages endpoint
   */
  async callTool(toolName, args = {}) {
    if (!this.sessionId) {
      throw new Error('Session not initialized. Call initialize() first.');
    }

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
        params: {
          name: toolName,
          arguments: args
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Tool call failed: ${response.status}`);
    }

    // Parse SSE response
    const responseText = await response.text();
    return this.parseSSEResponse(responseText);
  }

  /**
   * Step 3: Parse SSE stream response
   */
  parseSSEResponse(responseText) {
    const lines = responseText.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const jsonData = JSON.parse(line.substring(6));
          return jsonData;
        } catch (e) {
          console.warn('Failed to parse SSE data line:', line);
        }
      }
    }
    
    throw new Error('No valid JSON found in SSE response');
  }

  /**
   * Helper: List all invoices
   */
  async listInvoices() {
    return await this.callTool('listInvoices');
  }

  /**
   * Helper: Get specific invoice
   */
  async getInvoice(invoiceId) {
    return await this.callTool('getInvoice', { invoiceId });
  }

  /**
   * Helper: Create new invoice
   */
  async createInvoice(invoiceData) {
    return await this.callTool('createInvoice', invoiceData);
  }

  /**
   * Helper: Get total invoice amount for date range
   */
  async getTotalInvoiceAmount(startDate, endDate) {
    return await this.callTool('totalInvoiceAmount', { startDate, endDate });
  }
}

// Example usage:
async function adkExample() {
  const client = new McpSseClient();
  
  try {
    // Initialize session
    await client.initialize();
    
    // List all invoices
    const invoices = await client.listInvoices();
    console.log('Invoices response:', invoices.result.content[0].text);
    
    // Get first invoice details if available
    if (invoices.result.content[0].text.includes('Invoice')) {
      // Extract first invoice ID from response (simplified example)
      console.log('Invoice listing successful');
    }
    
    // Get total for this year
    const total = await client.getTotalInvoiceAmount('2024-01-01', '2024-12-31');
    console.log('Total response:', total.result.content[0].text);
    
  } catch (error) {
    console.error('ADK Integration Error:', error.message);
  }
}

// Run example (uncomment to test)
// adkExample();

export default McpSseClient; 