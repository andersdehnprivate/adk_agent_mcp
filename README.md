# Local ADK + MCP Agent Project

A lightweight, local chat interface that integrates OpenAI models with custom tools via the Model Context Protocol (MCP), built using Google's Agent Development Kit (ADK).

## 🚀 Features

- **Local Chat Interface**: Console-based and web-based chat
- **MCP Tool Integration**: Connect to local MCP servers for custom tools
- **OpenAI Model Support**: GPT-4o and other compatible models
- **Flexible Architecture**: Works with or without MCP server
- **Zero Cloud Dependencies**: Everything runs locally

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (or compatible model access)
- Optional: Local MCP server running on port 3000

## 🛠️ Installation

### Option 1: Automated Setup (Recommended)

1. **Clone/Download** this project
2. **Run the setup script**:
   ```bash
   python setup.py
   ```

### Option 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MCP_SERVER_URL=http://localhost:3000/mcp
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: MCP Server Configuration
MCP_SERVER_URL=http://localhost:3000/mcp
```

### MCP Server Setup

If you have a local MCP server:

1. Ensure it's running on the configured URL (default: `http://localhost:3000/mcp`)
2. The server should provide OpenAPI-compliant tool definitions
3. Tools should accept JSON payloads and return structured responses

## 🎯 Usage

### Basic Agent (No MCP Tools)

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run basic agent
python agent.py
```

### Enhanced Agent (With MCP Integration)

```bash
# Run agent with MCP integration
python agent_with_mcp.py
```

### Web Interface

```bash
# Activate virtual environment first
venv\Scripts\activate.ps1     # Windows PowerShell
venv\Scripts\activate         # Windows Command Prompt
source venv/bin/activate      # macOS/Linux

# Launch ADK web interface with proper directory structure
adk web agents

# This will start the web interface with both agents:
# - basic_agent (basic AI assistant)
# - mcp_agent (AI assistant with MCP integration)
```

The web interface will be available at: http://localhost:8000

**Note**: The web interface requires a specific directory structure where each agent is in its own subdirectory with `__init__.py` and `agent.py` files. This structure is already set up in the `agents/` directory.

### Testing

```bash
# Test basic setup
python test_basic.py

# Test web interface compatibility
python test_web_interface.py
```

## 💻 Usage Examples

### Console Interface

```
🚀 Starting ADK Agent with MCP Integration
==================================================
⚠️  MCP server URL not configured
==================================================
Type 'exit' to quit

✅ Agent initialized successfully!
⚠️  MCP tools are not available (basic mode)
You can now chat with the agent. Type 'exit' to quit.

User: Hello! What can you help me with?
Agent: Hello! I'm an AI assistant ready to help you with various tasks...

User: exit
👋 Goodbye!
```

### With MCP Tools

When MCP server is configured and running:

```
User: call listFiles with {"path": "."}
Agent: I'll help you list the files in the current directory...
[Tool execution results]

User: Please analyze the data using the analyzeCsv tool
Agent: I'll analyze the CSV data for you...
[Tool execution and analysis]
```

## 📁 Project Structure

```
adk-project/
├── agent.py                 # Basic agent (console interface)
├── agent_with_mcp.py        # Enhanced agent with MCP integration (console interface)
├── agents/                  # Web interface agent directory
│   ├── basic_agent/
│   │   ├── __init__.py
│   │   └── agent.py         # Basic agent for web interface
│   └── mcp_agent/
│       ├── __init__.py
│       └── agent.py         # MCP agent for web interface
├── requirements.txt         # Python dependencies
├── setup.py                 # Automated setup script
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore patterns
├── README.md               # This file
├── SPECIFICATION.md        # Detailed project specification
└── venv/                   # Virtual environment (created by setup)
```

## 🔍 Troubleshooting

### Common Issues

1. **ImportError: No module named 'google.adk'**
   ```bash
   pip install google-adk
   ```

2. **API Key Error**
   - Create `.env` file with your `OPENAI_API_KEY`
   - Ensure the key is valid and has appropriate permissions

3. **MCP Connection Failed**
   - Check if MCP server is running on configured URL
   - Verify server is accessible and returning valid responses
   - Agent will continue to work without MCP tools

4. **Web Interface Error: "No root_agent found"**
   - ✅ **FIXED**: Use `adk web agents` instead of `adk web`
   - The web interface requires a specific directory structure (see `agents/` directory)
   - Each agent must be in its own subdirectory with `__init__.py` and `agent.py` files
   - This structure is already set up in the project

4. **Python Version Error**
   - Ensure Python 3.8+ is installed
   - Use `python --version` to check

### Debug Mode

Run with verbose output:
```bash
python -v agent_with_mcp.py
```

## 🧪 Testing

### Test Basic Setup
```bash
python test_basic.py
```

### Test MCP Integration
```bash
python agent_with_mcp.py
```

### Test Web Interface
```bash
adk web
```

## 🔧 Development

### Adding New Tools

1. **MCP Tools**: Configure your MCP server with additional tools
2. **Custom Tools**: Extend the agent configuration in `agent_with_mcp.py`
3. **Built-in Tools**: Use ADK's built-in tools from `google.adk.tools`

### Customizing the Agent

Edit `agent_with_mcp.py` to:
- Change the model (e.g., from `gpt-4o` to `gpt-3.5-turbo`)
- Modify the instruction prompt
- Add additional toolsets
- Change connection parameters

### Example Customization

```python
# Custom agent with different model
agent = LlmAgent(
    name="custom_agent",
    model="gpt-3.5-turbo",
    instruction="You are a specialized assistant for...",
    tools=[
        # Add your custom tools here
    ]
)
```

## 🚀 Deployment

### Local Development
- Run directly with Python
- Use `adk web` for web interface
- Perfect for testing and development

### Production Considerations
- Use proper API key management
- Implement logging and monitoring
- Consider containerization for consistency
- Set up proper error handling

## 📚 Documentation

- **Specification**: See `SPECIFICATION.md` for detailed technical specifications
- **ADK Documentation**: https://google.github.io/adk-docs/
- **MCP Protocol**: Model Context Protocol documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes.

## 🔗 Related Links

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Need Help?** Check the troubleshooting section or review the specification document for detailed technical information. 