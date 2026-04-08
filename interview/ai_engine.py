import os
import requests
import json

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = "llama-3.3-70b-versatile"


def ai_evaluate_answer(question_text: str, user_answer: str):
    if not GROQ_API_KEY:
        return _fallback_response("GROQ_API_KEY not set in environment.")

    prompt = f"""You are a strict but fair technical interview coach evaluating a candidate's answer.

Question: {question_text}

Candidate's Answer: {user_answer}

Evaluate the answer and respond ONLY with a valid JSON object in this exact format, nothing else:
{{
  "score": <integer from 1 to 10>,
  "strengths": ["<specific strength 1>", "<specific strength 2>"],
  "weaknesses": ["<specific weakness 1>"],
  "improvements": ["<specific improvement suggestion 1>", "<specific improvement suggestion 2>"]
}}

Be specific to the question asked. Do not give generic feedback."""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 400,
            },
            timeout=30,
        )

        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code blocks if model wraps in them
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)

        return {
            "score": max(1, min(10, int(result.get("score", 5)))),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "improvements": result.get("improvements", []),
            "raw": content,
        }

    except json.JSONDecodeError:
        # Groq responded but not valid JSON — use raw text as feedback
        return {
            "score": 5,
            "strengths": [],
            "weaknesses": [],
            "improvements": [
                content if "content" in dir() else "Could not parse AI response."
            ],
            "raw": "",
        }
    except Exception as e:
        return _fallback_response(str(e))


def _fallback_response(reason: str):
    return {
        "strengths": [],
        "weaknesses": ["AI feedback temporarily unavailable."],
        "improvements": ["Please try again in a moment."],
        "score": 0,
        "raw": reason,
    }


def ai_generate_questions(role_name: str, count: int = 10):
    if not GROQ_API_KEY:
        return []

    prompt = f"""You are a technical interview coach. Generate {count} interview questions for a {role_name} role.

Respond ONLY with a valid JSON array in this exact format, nothing else:
[
  {{
    "text": "question here",
    "difficulty": "easy" or "medium" or "hard",
    "keywords": ["keyword1", "keyword2"]
  }}
]

Mix difficulties. Make questions specific and technical."""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        return json.loads(content)

    except Exception as e:
        return []
