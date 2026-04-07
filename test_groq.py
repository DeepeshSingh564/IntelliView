
import requests
import os

key = os.environ.get("GROQ_API_KEY")
print("Key found:", key[:10] if key else "NOT FOUND")

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "say hello"}], "max_tokens": 10}
)
print(r.status_code, r.text)