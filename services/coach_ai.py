# services/coach_ai.py
from __future__ import annotations
from typing import List, Tuple, Optional
from services.policy_index import PolicyIndex, PolicyHit

SYSTEM_BASE = """You are Vista, an expert leadership coach.
- First, prefer company policies when they apply. If a direct policy covers the user's question, follow it and cite the policy section(s) by name.
- If no direct policy applies, state that plainly and proceed with best-practice leadership guidance.
- Be concise, professional, supportive, and specific. Offer step-by-step options or scripts where helpful.
- Never invent policy. Do not contradict cited policy.
- End with 2-3 concrete next steps or a short checklist.
"""

POLICY_PREFIX = "The following policy snippets may be relevant:\n"
NO_POLICY_FOUND = "No directly relevant company policy snippet was found for this question."

def _format_hits(hits: List[PolicyHit]) -> str:
    lines = []
    for h in hits:
        lines.append(f"[{h.meta['doc_id']} › {h.meta['section']}] {h.text.strip()}")
    return "\n\n".join(lines)

class VistaCoach:
    def __init__(self, api_key: str, model: str, temperature: float, index: PolicyIndex):
        # Lazy import to avoid hard dependency if user hasn't installed yet
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("Please install openai>=1.0.0: pip install openai") from e
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = float(temperature)
        self.index = index

    def coach(
        self,
        user_input: str,
        history: List[Tuple[str, str]],
        strict_policy: bool = False,
        top_k: int = 4,
        min_score: float = 0.08,
    ) -> tuple[str, Optional[List[PolicyHit]]]:
        # 1) Retrieve policy snippets
        hits = self.index.search(user_input, k=top_k)
        relevant = [h for h in hits if h.score >= min_score]

        # 2) Compose system/instructions and context
        system = SYSTEM_BASE
        policy_block = POLICY_PREFIX + _format_hits(relevant) if relevant else NO_POLICY_FOUND

        if strict_policy and not relevant:
            # Refuse without policy basis
            msg = (
                "I couldn't find a policy section that directly covers this. "
                "With **Strict policy mode** on, I won't proceed without a reference. "
                "Try rephrasing or check with HR/Legal for guidance."
            )
            return msg, relevant

        # 3) Build messages: include brief history, then current question
        messages = []
        messages.append({"role": "system", "content": system})
        messages.append({"role": "system", "content": policy_block})

        # Limit history to last ~6 exchanges to keep it snappy
        for role, content in history[-12:]:
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_input})

        # 4) Call OpenAI
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        answer = resp.choices[0].message.content.strip()
        return answer, relevant
