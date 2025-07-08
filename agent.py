import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

# Load environment variables
load_dotenv()

# Basic agent configuration without MCP for initial testing
root_agent = LlmAgent(
    name="local_mcp_agent",
    model="gpt-4o",
    instruction="""
You are an AI assistant that will be enhanced with local tools via MCP.
For now, you can help with general questions and tasks.
When tools are available, you'll be able to invoke them to help users.
""",
    tools=[],  # Start with no tools for basic testing
)

# Keep agent variable for backward compatibility
agent = root_agent

# Console interface for testing
if __name__ == "__main__":
    print("🚀 Starting ADK Agent (Basic Mode)")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    try:
        from google.adk.runners import InMemoryRunner
        
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            print("❌ Please set your OPENAI_API_KEY in the .env file")
            print("Create a .env file with: OPENAI_API_KEY=your_actual_api_key")
            exit(1)
        
        # Create runner and start interactive session
        runner = InMemoryRunner()
        print("✅ Agent initialized successfully!")
        print("You can now chat with the agent. Type 'exit' to quit.")
        print()
        
        # Simple interactive loop
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            try:
                # Run the agent with user input
                result = runner.chat(agent, user_input)
                print(f"Agent: {result.response}")
                print()
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
        
    except ImportError as e:
        print(f"❌ Error importing ADK runners: {e}")
        print("Please ensure google-adk is installed: pip install google-adk")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("Please check your OPENAI_API_KEY environment variable") 