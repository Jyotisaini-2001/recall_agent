import os
import json
import re
import subprocess

from dotenv import load_dotenv

load_dotenv()


def _parse_json(text: str) -> dict:
    text = text.strip()
    # strip <think>...</think> blocks from reasoning models
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    # strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def _call_local_claude(prompt: str) -> tuple[dict, int]:
    import shutil
    claude_bin = shutil.which("claude") or "claude"
    result = subprocess.run(
        [claude_bin, "-p", prompt],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr.strip()}")
    if not result.stdout.strip():
        raise RuntimeError("claude CLI returned empty output")
    # estimate tokens: ~4 chars per token for prompt + response
    estimated_tokens = (len(prompt) + len(result.stdout)) // 4
    return _parse_json(result.stdout), estimated_tokens


def _call_minimax(prompt: str) -> tuple[dict, int]:
    import httpx

    api_key = os.getenv("MINIMAX_API_KEY")
    model = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
    url = "https://api.minimax.io/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}

    resp = httpx.post(url, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "choices" not in data:
        raise RuntimeError(f"Minimax unexpected response: {data}")
    content = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens", 0)
    return _parse_json(content), tokens


def _call_gemini(prompt: str) -> tuple[dict, int]:
    import httpx

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = httpx.post(url, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
    return _parse_json(content), tokens


def _call_anthropic(prompt: str) -> tuple[dict, int]:
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model, max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    content = resp.content[0].text
    tokens = resp.usage.input_tokens + resp.usage.output_tokens
    return _parse_json(content), tokens


def call(prompt: str) -> tuple[dict, int, str]:
    """
    Returns (parsed_json, tokens_used, provider_name).
    Primary: local Claude Code CLI (no API key needed).
    Fallback: minimax → gemini → anthropic (if keys set in .env).
    """
    # Try local Claude Code first
    try:
        result, tokens = _call_local_claude(prompt)
        return result, tokens, "claude-local"
    except Exception as e:
        local_error = e

    print(f"[WARN] Local Claude unavailable ({local_error}), trying API providers...")

    api_providers = [
        ("minimax",   os.getenv("MINIMAX_API_KEY"),   _call_minimax),
        ("gemini",    os.getenv("GEMINI_API_KEY"),     _call_gemini),
        ("anthropic", os.getenv("ANTHROPIC_API_KEY"),  _call_anthropic),
    ]

    last_error = None
    for name, key, fn in api_providers:
        if not key:
            continue
        try:
            result, tokens = fn(prompt)
            return result, tokens, name
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All providers failed. Local error: {local_error}. Last API error: {last_error}")
