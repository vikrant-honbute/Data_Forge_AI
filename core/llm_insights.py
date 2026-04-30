from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib import error, request

from dotenv import load_dotenv

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"


def _post_json(url: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8") if exc.fp else str(exc)
        raise RuntimeError(f"Groq API error {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Groq API connection error: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from Groq: {body}") from exc


def _extract_message_content(response: Dict[str, Any]) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Unexpected response structure: {response}") from exc


def generate_insights(profile: dict) -> dict:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment or .env")

    model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return JSON with keys summary and risks only.",
            },
            {
                "role": "user",
                "content": f"Profile: {json.dumps(profile, ensure_ascii=True)}",
            },
        ],
        "temperature": 0.2,
        "max_tokens": 400,
        "response_format": {"type": "json_object"},
    }

    response = _post_json(GROQ_API_URL, payload, api_key)
    content = _extract_message_content(response)

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned non-JSON content: {content}") from exc

    if not isinstance(result, dict):
        raise ValueError("Groq response JSON is not an object")
    if "summary" not in result or "risks" not in result:
        raise ValueError("Groq response missing summary or risks")

    return {
        "summary": result["summary"],
        "risks": result["risks"],
    }


def generate_explanation(suggestion: dict, profile_summary: dict) -> dict:
    fallback = {
        "explanation": "LLM explanation unavailable. Review the suggestion details manually.",
        "impact": "No impact assessment available.",
    }

    try:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return fallback

        model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return JSON with keys explanation and impact only. "
                        "No code, no steps, keep it short."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Profile summary: "
                        + json.dumps(profile_summary, ensure_ascii=True)
                        + "\nColumn: "
                        + str(suggestion.get("column"))
                        + "\nIssue: "
                        + str(suggestion.get("issue"))
                        + "\nSuggested action: "
                        + str(suggestion.get("action"))
                        + "\nExplain why this action is recommended and its impact."
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 200,
            "response_format": {"type": "json_object"},
        }

        response = _post_json(GROQ_API_URL, payload, api_key)
        content = _extract_message_content(response)
        result = json.loads(content)
        if not isinstance(result, dict):
            return fallback
        if "explanation" not in result or "impact" not in result:
            return fallback

        return {
            "explanation": result["explanation"],
            "impact": result["impact"],
        }
    except Exception:
        return fallback
