# services/people.py
"""
Mock data + helpers for the People page.

Make sure there is a file `services/__init__.py` so this folder is a package.
"""

from __future__ import annotations
from typing import Dict, List, Optional

import random
import datetime as dt
from pathlib import Path
import streamlit as st


import base64
from mimetypes import guess_type



ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "employees"

# ----------------------------
# Mock Directory / Generators
# ----------------------------

@st.cache_data(show_spinner=False)
def list_employees() -> List[Dict]:
    """Return six mock employees. Cached for fast reruns."""
    skills = [
        "Python", "Go", "TypeScript", "React", "Data Modeling",
        "Systems Design", "SRE", "Product Thinking", "Leadership",
        "UX Writing", "Prompt Engineering", "SQL"
    ]

    today = dt.date.today()
    data = [
        _mk_employee(
            id="e01", name="Ava Chen", role="Senior Backend Engineer",
            dept="Platform", manager="You", tz="America/Los_Angeles",
            start=today - dt.timedelta(days=820), photo_emoji="🛠️",
            okr_progress=72, morale=("High", "+1"), workload=("Busy", "↗︎"),
            skills=random.sample(skills, 4),
        ),
        _mk_employee(
            id="e02", name="Ben Garcia", role="Product Designer",
            dept="Design", manager="You", tz="America/Los_Angeles",
            start=today - dt.timedelta(days=420), photo_emoji="🎨",
            okr_progress=58, morale=("Stable", "0"), workload=("Normal", "→"),
            skills=random.sample(skills, 4),
        ),
        _mk_employee(
            id="e03", name="Camila Singh", role="Data Scientist",
            dept="Analytics", manager="You", tz="America/Chicago",
            start=today - dt.timedelta(days=230), photo_emoji="📊",
            okr_progress=64, morale=("Dip", "-1"), workload=("Busy", "↗︎"),
            skills=random.sample(skills, 4),
        ),
        _mk_employee(
            id="e04", name="Diego Alvarez", role="Frontend Engineer",
            dept="Web", manager="You", tz="America/New_York",
            start=today - dt.timedelta(days=1100), photo_emoji="🧩",
            okr_progress=81, morale=("High", "+2"), workload=("Normal", "→"),
            skills=random.sample(skills, 4),
        ),
        _mk_employee(
            id="e05", name="Ella Morgan", role="Engineering Manager",
            dept="Platform", manager="You", tz="America/Los_Angeles",
            start=today - dt.timedelta(days=1500), photo_emoji="🧭",
            okr_progress=69, morale=("Stable", "0"), workload=("Underutilized", "↘︎"),
            skills=random.sample(skills, 4),
        ),
        _mk_employee(
            id="e06", name="Farid Rahman", role="QA Lead",
            dept="Quality", manager="You", tz="America/Los_Angeles",
            start=today - dt.timedelta(days=350), photo_emoji="🧪",
            okr_progress=54, morale=("Dip", "-2"), workload=("Busy", "↗︎"),
            skills=random.sample(skills, 4),
        ),
    ]
    return data

'''
def _photo_path_for(emp_id: str) -> Optional[str]:
    """Return a relative path to an employee photo if it exists, else None."""
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = ASSETS_DIR / f"{emp_id}{ext}"
        if p.exists():
            # Return a path relative to the repo root so Streamlit can serve it
            return str(p)
    return None
'''
'''
def _photo_path_for(emp_id: str) -> Optional[str]:
    # Return URL path for Streamlit static files
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = f"./static/employees/{emp_id}{ext}"
        if (ASSETS_DIR / f"{emp_id}{ext}").exists():
            return p
    print(p)
    return None
'''


def _photo_path_for(emp_id: str) -> Optional[str]:
    """Return an absolute filesystem path Streamlit can open with st.image."""
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = ASSETS_DIR / f"{emp_id}{ext}"
        if p.exists():
            return str(p)  # absolute path
    return None

def _mk_employee(
    id: str,
    name: str,
    role: str,
    dept: str,
    manager: str,
    tz: str,
    start: dt.date,
    photo_emoji: str,
    okr_progress: int,
    morale: tuple[str, str],
    workload: tuple[str, str],
    skills: List[str],
) -> Dict:
    today = dt.date.today()
    tenure_days = (today - start).days
    tenure_years = tenure_days // 365
    tenure_months = (tenure_days % 365) // 30
    tenure_human = f"{tenure_years}y {tenure_months}m"

    return {
        "id": id,
        "name": name,
        "role": role,
        "dept": dept,
        "manager": manager,
        "email": f"{name.lower().replace(' ', '.')}@mentorvista.example",
        "slack": f"@{name.split()[0].lower()}",
        "phone": "(555) 555-0101",
        "timezone": tz,
        "start_date": start.isoformat(),
        "tenure_human": tenure_human,
        # NEW: photo_path (local) and emoji fallback
        "photo_path": _photo_path_for(id),
        "photo_emoji": photo_emoji,
        "okr_progress": okr_progress,
        "morale": {"label": morale[0], "delta": morale[1]},
        "workload": {"label": workload[0], "delta": workload[1]},
        "skills": skills,
    }


# ----------------------------
# Lookup helpers
# ----------------------------

@st.cache_data(show_spinner=False)
def get_employee_by_id(emp_id: str) -> Dict:
    for e in list_employees():
        if e["id"] == emp_id:
            return e
    raise KeyError(f"Employee not found: {emp_id}")


# ----------------------------
# Render helpers (UI)
# ----------------------------

def _pill(text: str) -> str:
    return (
        "<span style='padding:3px 8px;border-radius:999px;"
        "background:#EEF2FF;border:1px solid #C7D2FE;font-size:12px'>"
        f"{text}</span>"
    )



def _img_html(path: Optional[str], emoji: str) -> str:
    """Return an <img> tag (base64) or an emoji fallback, sized 72x72 circular."""
    if path:
        try:
            mime, _ = guess_type(path)
            mime = mime or "image/png"
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return (
                f"<img alt='' src='data:{mime};base64,{b64}' "
                "style='width:72px;height:72px;border-radius:50%;"
                "object-fit:cover;display:block'/>"
            )
        except Exception:
            pass
    return f"<div style='font-size:42px;line-height:1'>{emoji}</div>"

'''
def employee_summary_card(emp: Dict) -> None:
    with st.container():
        st.markdown(
            "<div style='border:1px solid #e5e7eb; padding:16px 18px; border-radius:16px;'>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([1, 5])
        with col1:
            if emp.get("photo_path"):
                st.image(emp["photo_path"], width=72)
            else:
                st.markdown(
                    f"<div style='font-size:42px; line-height:1'>{emp['photo_emoji']}</div>",
                    unsafe_allow_html=True,
                )
        with col2:
            st.markdown(f"**{emp['name']}**")
            st.markdown(
                f"<span style='color:#4b5563'>{emp['role']} • {emp['dept']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"{_pill(emp['email'])} &nbsp;•&nbsp; {_pill(emp['slack'])} &nbsp;•&nbsp; {_pill(emp['phone'])}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"{_pill(emp['timezone'])} {_pill('Tenure: ' + emp['tenure_human'])}",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
'''

def employee_summary_card(emp: Dict) -> None:
    img_html = _img_html(emp.get("photo_path"), emp["photo_emoji"])

    box_html = f"""
    <div style="
        display:flex;gap:14px;align-items:center;
        border:1px solid #e5e7eb;padding:16px 18px;border-radius:16px;">
        <div>{img_html}</div>
        <div>
            <div style="font-weight:700;font-size:18px">{emp['name']}</div>
            <div style="color:#4b5563">{emp['role']} • {emp['dept']}</div>
            <div style="margin-top:6px;color:#6b7280">
                {_pill(emp['email'])} &nbsp;•&nbsp; {_pill(emp['slack'])} &nbsp;•&nbsp; {_pill(emp['phone'])}
            </div>
            <div style="margin-top:8px;display:flex;gap:8px;">
                {_pill(emp['timezone'])} {_pill('Tenure: ' + emp['tenure_human'])}
            </div>
        </div>
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)







# ----------------------------
# Data providers (mock)
# ----------------------------

def get_projects_for_employee(emp_id: str) -> List[Dict]:
    rng = random.Random(emp_id)  # stable per employee
    samples = [
        {
            "name": "Service Mesh Upgrade",
            "status": rng.choice(["On Track", "At Risk", "Delayed"]),
            "summary": "Upgrade Envoy sidecars and roll out mTLS cluster-wide.",
            "progress": rng.randint(40, 90) / 100,
            "last_update": "2025-09-15",
        },
        {
            "name": "Billing Latency SLO",
            "status": rng.choice(["On Track", "At Risk", "Delayed"]),
            "summary": "Reduce p95 from 900ms → 450ms via queue backpressure and caching.",
            "progress": rng.randint(20, 85) / 100,
            "last_update": "2025-09-12",
        },
    ]
    if emp_id in ("e02", "e04"):
        samples.append({
            "name": "Design System v3",
            "status": rng.choice(["On Track", "At Risk", "Delayed"]),
            "summary": "Refactor tokens, accessibility, and theming storybook.",
            "progress": rng.randint(30, 95) / 100,
            "last_update": "2025-09-10",
        })
    return samples


def get_okrs_for_employee(emp_id: str) -> List[Dict]:
    rng = random.Random("okr-" + emp_id)
    return [
        {
            "title": "Cut incident MTTR by 25%",
            "owner": "Q3 Engineering",
            "desc": "Adopt runbooks, alerts, and chaos drills.",
            "progress": rng.randint(50, 90) / 100,
            "target": "Sep 30, 2025",
            "updated": "2025-09-14",
        },
        {
            "title": "Launch self-serve data portal",
            "owner": "Analytics",
            "desc": "Data models, governance, and doc portal.",
            "progress": rng.randint(30, 80) / 100,
            "target": "Oct 31, 2025",
            "updated": "2025-09-13",
        },
    ]


def get_pulse_for_employee(emp_id: str) -> Dict:
    rng = random.Random("pulse-" + emp_id)
    return {
        "score": rng.randint(6, 9),
        "delta": rng.uniform(-1.5, 1.5),
        "collab": rng.randint(6, 10),
        "stress": rng.randint(3, 7),
    }


def get_timeoff_for_employee(emp_id: str) -> Dict:
    rng = random.Random("to-" + emp_id)
    base = dt.date(2025, 9, 1)
    upcomings = [
        {"label": "PTO", "start": (base + dt.timedelta(days=rng.randint(5, 20))).isoformat(),
         "end": (base + dt.timedelta(days=rng.randint(21, 25))).isoformat()},
    ]
    return {"balance_days": rng.randint(6, 18), "upcoming": upcomings}


def get_kudos_for_employee(emp_id: str) -> List[Dict]:
    rng = random.Random("kudos-" + emp_id)
    msgs = [
        "Crushed the on-call rotation and wrote great postmortem notes.",
        "Led a thoughtful design review — clear tradeoffs and risks.",
        "Unblocked the team by pairing and documenting setup steps.",
    ]
    names = ["Priya", "Jon", "Marta", "Lee"]
    out = []
    for _ in range(rng.randint(1, 3)):
        out.append({
            "from": rng.choice(names),
            "date": f"2025-09-{rng.randint(10, 19)}",
            "message": rng.choice(msgs),
        })
    return out


# ----------------------------
# AI coaching (mocked rules)
# ----------------------------

def get_ai_coaching_tips(emp: Dict) -> Dict:
    tips = []
    checkins = []

    morale = emp["morale"]["label"].lower()
    workload = emp["workload"]["label"].lower()
    okr = emp["okr_progress"]

    if "dip" in morale:
        tips.append("Acknowledge recent challenges; set a small, winnable goal this week.")
        checkins.append("What’s one blocker I can remove before Friday?")
    elif "high" in morale:
        tips.append("Offer a stretch project or mentoring opportunity.")
        checkins.append("Who could benefit from your mentorship this sprint?")

    if "busy" in workload:
        tips.append("Re-prioritize tasks and defer non-essentials; protect focus time.")
        checkins.append("Which task this week has the worst ROI to drop?")
    elif "underutilized" in workload:
        tips.append("Increase scope gradually; align with an OKR where they can lead.")
        checkins.append("Is there a domain you’re eager to own this quarter?")

    if okr < 60:
        tips.append("Align weekly tasks to OKRs; review measurable outcomes in 1:1s.")
        checkins.append("Which OKR key result will move most with 2 hours of work?")

    tips = list(dict.fromkeys(tips))
    checkins = list(dict.fromkeys(checkins))
    return {"manager_tips": tips, "checkins": checkins}
