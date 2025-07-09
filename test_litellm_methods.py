import os
from dotenv import load_dotenv
import inspect

# Load environment variables
load_dotenv()

print("🔍 LiteLLM Methods Investigation")
print("=" * 50)

try:
    from google.adk.models.lite_llm import LiteLlm
    
    # Create model
    model = LiteLlm(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=100
    )
    
    print("✅ LiteLLM model created")
    
    # Get all methods
    methods = [m for m in dir(model) if not m.startswith('_')]
    
    print(f"\n📋 Available methods ({len(methods)}):")
    for method in methods:
        try:
            attr = getattr(model, method)
            if callable(attr):
                sig = inspect.signature(attr)
                is_async = inspect.iscoroutinefunction(attr)
                print(f"   📝 {method}{sig} {'(async)' if is_async else ''}")
            else:
                print(f"   📊 {method}: {type(attr).__name__}")
        except Exception as e:
            print(f"   ❌ {method}: Error - {e}")
    
    print("\n🔧 Testing potential methods:")
    
    # Test generate_content_async
    if hasattr(model, 'generate_content_async'):
        print("   🔧 Testing generate_content_async...")
        try:
            method = getattr(model, 'generate_content_async')
            print(f"      Type: {type(method)}")
            print(f"      Callable: {callable(method)}")
            print(f"      Is coroutine: {inspect.iscoroutinefunction(method)}")
            
            if inspect.iscoroutinefunction(method):
                print("      ✅ This is a proper async method")
            else:
                print("      ❌ This is NOT a proper async method")
                
        except Exception as e:
            print(f"      ❌ Error testing method: {e}")
    
    # Test __call__ method
    if hasattr(model, '__call__'):
        print("   🔧 Testing __call__ method...")
        try:
            method = getattr(model, '__call__')
            sig = inspect.signature(method)
            print(f"      Signature: {sig}")
            print(f"      Is coroutine: {inspect.iscoroutinefunction(method)}")
        except Exception as e:
            print(f"      ❌ Error testing __call__: {e}")
    
    # Test agenerate method
    if hasattr(model, 'agenerate'):
        print("   🔧 Testing agenerate method...")
        try:
            method = getattr(model, 'agenerate')
            sig = inspect.signature(method)
            print(f"      Signature: {sig}")
            print(f"      Is coroutine: {inspect.iscoroutinefunction(method)}")
        except Exception as e:
            print(f"      ❌ Error testing agenerate: {e}")
    
    print("\n🎯 Investigation complete!")
    
except Exception as e:
    print(f"❌ Error during investigation: {e}")
    import traceback
    traceback.print_exc() 