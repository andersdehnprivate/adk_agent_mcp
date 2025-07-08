import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv()

# Basic agent configuration for web interface
root_agent = LlmAgent(
    name="basic_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction="""
You are a basic AI assistant powered by the Agent Development Kit (ADK).
You can help with general questions and tasks.
You provide helpful, accurate, and friendly responses.
""",
    tools=[],
) 