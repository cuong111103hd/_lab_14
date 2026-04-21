import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[{"role": "user", "content": "Ping"}],
        max_tokens=5
    )
    print("SUCCESS: gpt-5.4-nano is available!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"FAILED: gpt-5.4-nano is not available via this API key. Error: {e}")
