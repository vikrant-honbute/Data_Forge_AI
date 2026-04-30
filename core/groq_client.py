from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from groq import Groq

DEFAULT_MODEL = "llama-3.1-8b-instant"


def _get_client() -> Groq | None:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def generate_llm_explanation(suggestion: dict) -> dict:
    fallback = {
        "explanation": "LLM explanation unavailable. Review the suggestion details manually.",
        "impact": "No impact assessment available.",
    }

    client = _get_client()
    if client is None:
        return fallback

    column = suggestion.get("column")
    issue = suggestion.get("type") or suggestion.get("issue")
    action = suggestion.get("action")

    prompt = (
        "You are a data analyst assistant.\n\n"
        "Given:\n"
        f"* Column: {column}\n"
        f"* Issue: {issue}\n"
        f"* Action: {action}\n\n"
        "Explain:\n"
        "1. Why this action is recommended\n"
        "2. What impact it will have\n\n"
        "Return JSON only in this format:\n"
        '{"explanation": "...", "impact": "..."}'
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            return fallback

        if not isinstance(result, dict):
            return fallback
        if "explanation" not in result or "impact" not in result:
            return fallback
        return {"explanation": result["explanation"], "impact": result["impact"]}
    except Exception:
        return fallback
