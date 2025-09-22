from typing import Dict, List
from services.policy_index import get_policy_index

def summarize_standups(digest: Dict) -> Dict:
    wins = [f"{c['name']}: burned down backlog by 12%" for c in digest.get('channels', [])][:3]
    risks = [f"{c['name']}: after-hours {c['after_hours_pct']}%" for c in digest.get('channels', [])][:3]
    next_steps = ["Clarify handoff process in #proj-alpha", "Assign owner for flaky tests", "Schedule retro if risks persist"]
    return {"wins": wins, "risks": risks, "next": next_steps}

def list_prs_needing_attention(tasks: Dict) -> List[Dict]:
    return [pr for pr in tasks.get("prs", []) if pr.get("status") in {"review_requested", "open"}]

def draft_followup(item: Dict) -> str:
    if item.get("type") == "pr":
        age = item.get("age_days", "?")
        title = item.get("title", "this PR")
        return f"Hey team — gentle nudge on **{title}**. It's been open for {age} day(s). Could someone take a look today? Thanks!"
    return "Following up on this — can we move it forward?"

def prep_one_on_one(report: Dict, digest: Dict, company: str = "mentorvista") -> Dict:
    idx = get_policy_index(company)
    hits = idx.search("1:1 check-ins documentation HRIS", k=3)
    cites = [{"doc": h.doc_id, "section": h.section, "excerpt": (h.text[:220] + ("..." if len(h.text) > 220 else ""))} for h in hits]
    agenda = [
        f"Wins since last 1:1 (projects, impact)",
        f"Blockers & support needed",
        f"Growth toward goals: {', '.join(report.get('goals', [])[:2])}",
        f"Next sprint priorities & ownership"
    ]
    growth = "Delegation and ownership: identify one task to fully own end-to-end this sprint."
    commitments = ["Agree on one measurable outcome for next week", "Schedule follow-up date in HRIS notes"]
    return {"agenda": agenda, "growth_topic": growth, "commitments": commitments, "policy_citations": cites}
