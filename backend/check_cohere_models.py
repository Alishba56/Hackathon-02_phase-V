"""
Check available Cohere models
"""
from cohere_client import get_cohere_client

try:
    client = get_cohere_client()

    # Try to list available models
    print("Attempting to get available models...")

    # Try different model names that might be current
    test_models = [
        "command-r-08-2024",
        "command-r7b-12-2024",
        "command-r-03-2024",
        "command",
        "command-light",
        "command-nightly",
        "command-r-plus-08-2024"
    ]

    print("\nTesting models with a simple chat call:")
    for model in test_models:
        try:
            response = client.chat(
                message="Hello",
                model=model
            )
            print(f"[OK] {model} - WORKS!")
            break
        except Exception as e:
            error_msg = str(e)
            if "was removed" in error_msg or "404" in error_msg:
                print(f"[FAIL] {model} - Deprecated/Not Found")
            else:
                print(f"[FAIL] {model} - Error: {error_msg[:100]}")

except Exception as e:
    print(f"Error: {e}")
