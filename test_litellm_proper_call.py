import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 LiteLLM Proper Call Test")
print("=" * 50)

async def test_proper_call():
    try:
        from google.adk.models.lite_llm import LiteLlm
        from google.adk.core.llm_request import LlmRequest
        
        # Create model
        model = LiteLlm(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=100
        )
        
        print("✅ LiteLLM model created")
        
        # Create proper LlmRequest
        print("🔧 Creating LlmRequest...")
        
        # Create a simple request
        request = LlmRequest(
            messages=[{"role": "user", "content": "Hello! Just say 'Hi' back."}]
        )
        
        print("✅ LlmRequest created")
        print(f"   Request: {request}")
        
        # Call generate_content_async
        print("🔧 Calling generate_content_async...")
        
        # This returns an async generator
        async_gen = model.generate_content_async(request, stream=False)
        
        print("✅ Async generator created")
        
        # Collect results
        responses = []
        async for response in async_gen:
            print(f"   📝 Response: {response}")
            responses.append(response)
            
        print(f"✅ Completed! Got {len(responses)} responses")
        
        if responses:
            print(f"   💬 Final response: {responses[-1]}")
            
        return responses
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Run test
asyncio.run(test_proper_call()) 