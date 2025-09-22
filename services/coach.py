# services/coach.py
from __future__ import annotations
from typing import Dict, Any, List
from openai import OpenAI
import json

from .policy_index import PolicyIndex, PolicyHit

client = OpenAI()

# Retrieval / grounding tuning
TOP_K = 5
MIN_POLICY_SCORE_BASE = 0.12
MIN_POLICY_SCORE_STRICT = 0.22
CATALOG_EXTRA_MARGIN = 0.10  # require stronger score for catalogs

# Singleton index (built in the Streamlit page at runtime)
IDX: PolicyIndex = PolicyIndex()

SYSTEM_PROMPT = """You are MentorVista, a pragmatic leadership coach.
Your first duty is to apply the company's official policies when they are clearly relevant.
When no relevant policy is found, say so plainly and provide balanced, practical coaching
based on widely accepted management best practices.

Rules:
- If policy excerpts are provided, cite them briefly (e.g., “Policy Handbook §3.2”).
- Never invent policy language. If unsure, say you're unsure and give general guidance.
- Be concise, kind, and action-oriented; avoid legal advice.
- Flag sensitive cases (harassment, discrimination, safety, legal risk) for HR escalation.
- Always output valid JSON with the exact keys specified.
"""

def _format_policy_context(hits: List[PolicyHit]) -> str:
    lines = []
    for h in hits:
        tag = h.meta.get("section") or h.meta.get("source_title") or h.meta.get("source") or f"chunk-{h.meta.get('index')}"
        lines.append(f"- [{tag}] (score={h.score:.2f}) {h.text}")
    return "\n".join(lines)

def get_coaching(
    situation: str,
    persona: str = "General",
    target: str = "Clarity",
    company: str = "",
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Returns a JSON-friendly dict:
    {
      'grounding': 'policy' | 'general',
      'quick_take': str,
      'reasoning': str,
      'steps': [str],
      'risks': [str],
      'policy_refs': [{'source':..., 'source_title':..., 'section':..., 'score':...}],
      'debug': {...}
    }
    """
    # 1) Retrieve policy hits
    hits = IDX.search(situation, k=TOP_K)
    top = hits[0] if hits else None
    min_score = MIN_POLICY_SCORE_STRICT if strict else MIN_POLICY_SCORE_BASE

    # 2) Decide if we truly found a relevant policy
    #    - Catalogs count only if score is comfortably above threshold
    #    - Non-catalog policy counts if score >= threshold
    policy_found = False
    if top:
        is_catalog = bool(top.meta.get("is_catalog", False))
        if not is_catalog and top.score >= min_score:
            policy_found = True
        elif is_catalog and top.score >= (min_score + CATALOG_EXTRA_MARGIN):
            policy_found = True

    policy_context = _format_policy_context(hits) if hits else "(no matches)"
    grounding_note = (
        "Relevant policy excerpts were found and provided below."
        if policy_found else
        "No clearly relevant policy was found. Provide general coaching."
    )

    # 3) Build the model prompt
    user_prompt = f"""
Company: {company or "N/A"}
Persona (who's involved): {persona}
Coaching goal: {target}
Situation: {situation}

Grounding status: {"POLICY" if policy_found else "GENERAL_FALLBACK"}
{grounding_note}

Policy excerpts (top {TOP_K}):
{policy_context}

Output JSON with these keys:
- quick_take: one-paragraph TL;DR that references policy if applicable.
- reasoning: 3–6 sentences of rationale. If no policy found, say so first.
- steps: 3–7 concrete next actions tailored to the situation.
- risks: 2–5 pitfalls or watchouts.
- policy_refs: list of objects with source/source_title/section/score for any policy you used (empty if none).
"""

    # 4) Model call (response_format enforces valid JSON)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = completion.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        # Fallback: wrap as minimal JSON if provider ever misbehaves
        data = {
            "quick_take": content,
            "reasoning": "",
            "steps": [],
            "risks": [],
            "policy_refs": [],
        }

    # 5) Add explicit grounding flag
    data["grounding"] = "policy" if policy_found else "general"

    # 6) Normalize policy_refs; enrich from hits if missing
    if "policy_refs" not in data or not isinstance(data["policy_refs"], list):
        data["policy_refs"] = []

    if policy_found and not data["policy_refs"]:
        data["policy_refs"] = [
            {
                "source": h.meta.get("source"),
                "source_title": h.meta.get("source_title"),
                "section": h.meta.get("section"),
                "score": round(h.score, 3),
            }
            for h in hits[:3]
        ]

    # 7) Debug info to tune thresholds
    data["debug"] = {
        "top_score": round(top.score, 3) if top else 0.0,
        "min_threshold": min_score,
        "top_source": top.meta.get("source_title") if top else None,
        "top_section": top.meta.get("section") if top else None,
        "top_is_catalog": bool(top.meta.get("is_catalog", False)) if top else None,
    }

    return data
