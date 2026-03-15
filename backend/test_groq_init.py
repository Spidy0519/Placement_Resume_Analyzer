import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(f"Using API Key: {api_key[:10]}...")

try:
    client = Groq(api_key=api_key)
    print("SUCCESS: Groq client initialized.")
    print("Testing chat completion...")
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "test"}]
    )
    print("SUCCESS: Response received.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
