import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import threading
import sys

# Load environment variables
load_dotenv()

print("🔍 LiteLLM Simple Test")
print("=" * 50)

print("🔧 Step 1: Testing LiteLLM import...")
try:
    from google.adk.models.lite_llm import LiteLlm
    print("✅ LiteLLM import successful")
except Exception as e:
    print(f"❌ LiteLLM import failed: {e}")
    sys.exit(1)

print("\n🔧 Step 2: Creating LiteLLM model...")
try:
    model = LiteLlm(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=100
    )
    print("✅ LiteLLM model created")
except Exception as e:
    print(f"❌ LiteLLM model creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔧 Step 3: Testing model call with timeout...")
try:
    # Simple synchronous call with timeout
    messages = [{"role": "user", "content": "Say Hi"}]
    
    print("   🔧 Making generate_content call...")
    
    # Use asyncio.wait_for to add timeout
    async def test_sync():
        # Try to call synchronous method in thread
        import concurrent.futures
        
        def sync_call():
            return model.generate_content(messages)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sync_call)
            result = future.result(timeout=20)  # 20 second timeout
            return result
    
    result = asyncio.run(test_sync())
    print(f"✅ Synchronous call successful: {result}")
    
except Exception as e:
    print(f"❌ Model call failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🔧 Step 4: Testing async model call...")
try:
    async def test_async():
        messages = [{"role": "user", "content": "Say Hi"}]
        result = await asyncio.wait_for(
            model.generate_content_async(messages),
            timeout=20
        )
        return result
    
    result = asyncio.run(test_async())
    print(f"✅ Async call successful: {result}")
    
except Exception as e:
    print(f"❌ Async model call failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test completed!") 