from typing import Dict, List, Optional
from services.policy_index import get_policy_index
from utils.prompts import COACH_SYSTEM
from services.llm import call_openai_json

def _format_policy_citations(chunks) -> List[Dict]:
    cites = []
    for c in chunks[:3]:
        cites.append({
            "doc": c.doc_id,
            "section": c.section,
            "excerpt": c.text[:500] + ("..." if len(c.text) > 500 else "")
        })
    return cites

def get_coaching(
    situation: str,
    persona: str,
    target: str,
    company: str = "mentorvista",
    strict: bool = True,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict:
    """
    Policy-aware coaching.
    - If api_key is provided, calls OpenAI and returns JSON.
    - If not, returns an offline stub (good for demos without keys).
    """
    idx = get_policy_index(company)
    hits = idx.search(situation, k=5)
    policy_citations = _format_policy_citations(hits)
    context_blocks = [f"[{c['doc']} › {c['section']}]\n{c['excerpt']}" for c in policy_citations]

    # Offline fallback (no API key)
    advice_offline = {
        "quick_take": "Use SBI and document feedback within 48 hours per policy.",
        "steps": [
            "Schedule a private 1:1 within 24–48 hours.",
            "Describe the specific behavior and its impact (SBI).",
            "Co-create a clear next step and a check-in date.",
            "Document the conversation in HRIS within 48 hours as required."
        ],
        "phrases": [
            "“In yesterday’s handoff (Situation), I noticed the API wasn’t versioned (Behavior). That caused a rollback (Impact). Let’s align on how to avoid this.”",
            "“What support would help you meet the expectation next week?”"
        ],
        "watchouts": [
            "Avoid discussing protected characteristics.",
            "If performance concerns persist, consult HR before a PIP (policy min. 30 days)."
        ],
        "policy_citations": policy_citations
    }

    if strict and not policy_citations:
        advice_offline.update({
            "quick_take": "Policy context unavailable—route to HR.",
            "steps": ["Pause action.", "Email HR with a summary.", "Follow interim guidance from HR."],
            "phrases": ["“I want to ensure we follow policy, looping HR for guidance.”"],
            "watchouts": ["Do not take irreversible action without HR."],
            "escalation_note": "No matching policy excerpt found."
        })

    if not api_key:
        return advice_offline

    user_prompt = (
        f"Persona: {persona}\n"
        f"Employee involved: {target}\n"
        f"Situation described by manager: {situation}\n\n"
        "Respond with JSON keys: quick_take, steps (3–6), phrases (2–5), watchouts (2–5), "
        "policy_citations (re-list any you used by [doc › section]). If any request conflicts with policy, "
        "refuse and include 'escalation_note' with next steps."
    )

    out = call_openai_json(
        api_key=api_key,
        model=model,
        system_prompt=COACH_SYSTEM,
        user_prompt=user_prompt,
        context_blocks=context_blocks,
        history=history,
        temperature=0.2,
    )

    if not out.get("policy_citations"):
        out["policy_citations"] = policy_citations
    return out
