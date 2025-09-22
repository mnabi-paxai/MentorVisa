from typing import List, Dict, Optional
from openai import OpenAI
import json

def call_openai_json(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    context_blocks: Optional[List[str]] = None,
    history: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.2,
) -> Dict:
    """
    Calls OpenAI Chat Completions and asks for a JSON object back.
    history: list of {'role': 'user'|'assistant', 'content': '...'}
    Returns a Python dict.
    """
    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": system_prompt}]
    if context_blocks:
        messages.append({
            "role": "system",
            "content": "CONTEXT (policy excerpts):\n" + "\n\n".join(context_blocks)
        })
    if history:
        for turn in history:
            if turn.get("content"):
                messages.append({"role": turn.get("role", "user"), "content": turn["content"]})

    messages.append({"role": "user", "content": user_prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    text = resp.choices[0].message.content
    try:
        return json.loads(text)
    except Exception:
        # Fallback if the model returns plain text
        return {"quick_take": text, "steps": [], "phrases": [], "watchouts": [], "policy_citations": []}
