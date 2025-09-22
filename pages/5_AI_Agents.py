# ./pages/5_agents.py

import datetime as dt
from typing import Any, Dict, List
from pathlib import Path

import base64


import streamlit as st
from services.store import load_slack_digest, load_tasks, load_people

# Optional agent services: guarded so the page works without backends wired yet.
try:
    from services import agents as agent_svc  # noqa: F401
except Exception:  # pragma: no cover
    agent_svc = None

from services.agents import summarize_standups, list_prs_needing_attention, prep_one_on_one

# ---------------------------
# Page config & Header
# ---------------------------
st.title("AI Agents")
st.caption("Your operational AI workforce at a glance.")

def status_dot(color: str) -> str:
    return (
        "<span style='display:inline-block;width:8px;height:8px;border-radius:50%;"
        f"background:{color};margin-right:6px;vertical-align:middle'></span>"
    )

def get_agent_fn(name: str):
    return getattr(agent_svc, name, None) if agent_svc else None

# Load shared data
digest = load_slack_digest()
tasks = load_tasks()
people = load_people()

# ---------------------------
# Overview Cards (Minimal)
# ---------------------------
def agent_overview_cards():
    get_metrics = get_agent_fn("get_agent_metrics")
    metrics: List[Dict[str, Any]] = []
    if callable(get_metrics):
        try:
            metrics = get_metrics()
        except Exception:
            metrics = []
    if not metrics:
        metrics = [
            {"name": "Compliance Checker", "role": "Policy & Contract Scan", "status": "active", "key_metric_label": "Tasks (7d)", "key_metric_value": 48},
            {"name": "Form Filer", "role": "Portal Submission", "status": "in-progress", "key_metric_label": "Submissions (24h)", "key_metric_value": 12},
            {"name": "Audit Prep", "role": "Evidence Packaging", "status": "idle", "key_metric_label": "Packs (QTD)", "key_metric_value": 6},
        ]

    cols = st.columns(min(3, len(metrics)) or 1)
    for i, m in enumerate(metrics):
        with cols[i % len(cols)]:
            color = {"active": "#16a34a", "in-progress": "#f59e0b", "idle": "#6b7280", "flagged": "#ef4444"}.get(
                m.get("status", "idle"), "#6b7280"
            )
            st.markdown(
                f"""
                <div style="border:1px solid #eee;border-radius:16px;padding:14px 16px;margin-bottom:12px;">
                    <div style="font-size:14px;color:#6b7280;">{status_dot(color)}{m.get('role','')}</div>
                    <div style="font-size:18px;font-weight:600;margin-top:2px;">{m.get('name','')}</div>
                    <div style="display:flex;gap:6px;align-items:baseline;margin-top:10px;">
                        <div style="font-size:22px;font-weight:700;">{m.get('key_metric_value','–')}</div>
                        <div style="font-size:12px;color:#6b7280;">{m.get('key_metric_label','')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

agent_overview_cards()
st.divider()

# ---------------------------
# Tabs: Operations | Engineering Utilities | Activity
# ---------------------------
tab_ops, tab_eng, tab_activity = st.tabs(["Operations", "Engineering Utilities", "Activity"])

# ---------- helpers for image paths & rendering ----------
PROJECT_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "agents"
# Point fallbacks to files inside your repo; filenames must match those referenced below.
FALLBACKS = {
    "compliance_checker.png": PROJECT_ASSETS / "compliance_checker.png",
    "form_filer.png": PROJECT_ASSETS / "form_filer.png",
    "audit_prep.png": PROJECT_ASSETS / "audit_prep.png",
}

def resolve_img(name: str) -> Path | None:
    """
    Prefer local asset ./assets/agents/<name>.
    If not present, try the provided fallback path.
    Return a Path if exists, else None.
    """
    local = PROJECT_ASSETS / name
    if local.exists():
        return local
    fb = FALLBACKS.get(name)
    if fb and Path(fb).exists():
        return Path(fb)
    return None

def safe_image(path_or_none: Path | None, alt: str, *, height: int | None = None):
    """
    Render an image if present; otherwise show a minimal gray placeholder so UI never crashes.
    """
    if path_or_none and path_or_none.exists():
        st.image(str(path_or_none), use_container_width=True)
        return
    h = f"height:{height}px;" if height else ""
    st.markdown(
        f"""
        <div style="width:100%;{h}background:#f3f4f6;border:1px dashed #e5e7eb;
                    border-radius:12px;display:flex;align-items:center;justify-content:center;">
            <div style="color:#6b7280;font-size:13px;padding:16px;">{alt} image not found</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


import base64

def fixed_height_image(path_or_none: Path | None, alt: str, height: int = 160):
    if path_or_none and path_or_none.exists():
        data = path_or_none.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        st.markdown(
            f"""
            <img alt="{alt}" src="data:image/png;base64,{b64}"
                 style="width:100%;height:{height}px;object-fit:cover;border-radius:8px;display:block;" />
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="width:100%;height:{height}px;background:#f3f4f6;border:1px dashed #e5e7eb;
                        border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <div style="color:#6b7280;font-size:13px;padding:16px;">{alt} image not found</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------
# OPERATIONS TAB (image cards, minimalist)
# ---------------------------
with tab_ops:
    st.subheader("Operational Agents", help="Click an agent to open quick actions.")

    AGENT_CARDS = [
        {
            "name": "Compliance Checker",
            "role": "Scan & flag gaps",
            "image": resolve_img("compliance_checker.png"),
            "status": "active",
            "open_key": "open_cc",
        },
        {
            "name": "Form Filer",
            "role": "Validate & submit",
            "image": resolve_img("form_filer.png"),
            "status": "in-progress",
            "open_key": "open_ff",
        },
        {
            "name": "Audit Prep",
            "role": "Compile evidence",
            "image": resolve_img("audit_prep.png"),
            "status": "idle",
            "open_key": "open_ap",
        },
    ]

    cols = st.columns(3)
    for i, card in enumerate(AGENT_CARDS):
        with cols[i]:
            color = {"active": "#16a34a", "in-progress": "#f59e0b", "idle": "#6b7280", "flagged": "#ef4444"}.get(
                card["status"], "#6b7280"
            )

            with st.container(border=True):
                # header
                st.markdown(
                    f"<div style='font-size:13px;color:#6b7280;'>{status_dot(color)}{card['role']}</div>"
                    f"<div style='font-size:16px;font-weight:600;margin:2px 0 8px 0;color:#111827;'>{card['name']}</div>",
                    unsafe_allow_html=True,
                )
                # image (or placeholder)
               # safe_image(card["image"], alt=card["name"], height=160)
                fixed_height_image(card["image"], alt=card["name"], height=200)


                # Open button -> sets a real Streamlit state key
                if st.button("Open", key=f"btn_{card['open_key']}", use_container_width=True):
                    st.session_state[card["open_key"]] = True

    # Minimal drawers
    if st.session_state.get("open_cc"):
        with st.expander("Compliance Checker — quick actions", expanded=True):
            scope = st.text_input("Scope", value="drive://VendorContracts/2025", label_visibility="collapsed")
            review_mode = st.toggle("Require human review", value=True)
            run_cc = st.button("Run Scan", use_container_width=True)
            cc_fn = get_agent_fn("run_compliance_scan")
            if run_cc:
                with st.spinner("Scanning…"):
                    try:
                        findings = (
                            cc_fn(scope=scope, review_required=review_mode)
                            if callable(cc_fn)
                            else [{"doc": "Vendor_A_Master_Agreement.pdf", "issue": "Missing DP addendum", "severity": "High"}]
                        )
                        st.success(f"Found {len(findings)} item(s).")
                        for f in findings:
                            st.markdown(f"- **{f.get('doc','doc')}** — {f.get('issue','issue')} ({f.get('severity','')})")
                    except Exception as e:
                        st.error(f"Scan failed: {e}")

    if st.session_state.get("open_ff"):
        with st.expander("Form Filer — quick actions", expanded=True):
            form_type = st.selectbox("Form", ["W-9", "I-9", "State Compliance Report", "Vendor Onboarding"])
            dry_run = st.toggle("Dry-run", value=True)
            run_ff = st.button("Submit", use_container_width=True)
            ff_fn = get_agent_fn("file_form")
            if run_ff:
                with st.spinner("Submitting…"):
                    try:
                        result = (
                            ff_fn(form_type=form_type, payload_file=None, dry_run=dry_run)
                            if callable(ff_fn)
                            else {"status": "ok", "submission_id": "SUBM-2025-0912-XYZ"}
                        )
                        if result.get("status") == "ok":
                            st.success(f"Submitted ✓  ID: {result.get('submission_id')}")
                        else:
                            st.error(f"Submission failed: {result}")
                    except Exception as e:
                        st.error(f"Form filing error: {e}")

    if st.session_state.get("open_ap"):
        with st.expander("Audit Prep — quick actions", expanded=True):
            start = st.date_input("Start", value=dt.date.today().replace(day=1))
            end = st.date_input("End", value=dt.date.today())
            run_ap = st.button("Generate Pack", use_container_width=True)
            ap_fn = get_agent_fn("generate_audit_pack")
            if run_ap:
                with st.spinner("Packaging…"):
                    try:
                        pack = (
                            ap_fn(start=start, end=end, include=["Access Logs", "Approvals"])
                            if callable(ap_fn)
                            else {"status": "ok", "file_name": f"audit_pack_{start}_{end}.zip", "size_mb": 12.4}
                        )
                        if pack.get("status") == "ok":
                            st.success(f"Ready: {pack.get('file_name')}  ({pack.get('size_mb','–')} MB)")
                        else:
                            st.error(f"Audit prep failed: {pack}")
                    except Exception as e:
                        st.error(f"Audit prep error: {e}")

# ---------------------------
# ENGINEERING UTILITIES TAB (kept)
# ---------------------------
with tab_eng:
    st.subheader("Engineering Utilities", help="Existing demo utilities preserved.")
    with st.expander("Stand-up Summarizer", expanded=False):
        if st.button("Summarize last 24h", use_container_width=True):
            summary = summarize_standups(digest)
            st.markdown("**Wins**")
            for w in summary.get("wins", []):
                st.markdown(f"- {w}")
            st.markdown("**Risks**")
            for r in summary.get("risks", []):
                st.markdown(f"- {r}")
            st.markdown("**Next Steps**")
            for n in summary.get("next", []):
                st.markdown(f"- {n}")

    with st.expander("PRs Needing Attention", expanded=False):
        prs = list_prs_needing_attention(tasks)
        if not prs:
            st.caption("No PRs require attention.")
        for pr in prs:
            st.markdown(f"- PR #{pr['id']}: {pr['title']} (age: {pr['age_days']} days)")

    with st.expander("Prep a 1:1", expanded=False):
        names = {p['name']: p for p in people}
        name = st.selectbox("Select report", list(names.keys()))
        if st.button("Prepare 1:1 agenda", use_container_width=True):
            agenda = prep_one_on_one(names[name], digest, company="mentorvista")
            st.markdown("**Agenda**")
            for a in agenda.get("agenda", []):
                st.markdown(f"- {a}")
            st.markdown("**Growth Topic**\n- " + agenda.get("growth_topic", ""))
            st.markdown("**Policy Citations**")
            for c in agenda.get("policy_citations", []):
                st.markdown(f"- **[{c['doc']} › {c['section']}]** — {c['excerpt']}")

# ---------------------------
# ACTIVITY TAB
# ---------------------------
with tab_activity:
    st.subheader("Recent Activity")
    act_fn = get_agent_fn("get_activity_feed")
    feed: List[Dict[str, Any]] = []
    try:
        if callable(act_fn):
            feed = act_fn(limit=20)
    except Exception:
        feed = []

    if not feed:
        feed = [
            {"time": "10:23", "agent": "Form Filer", "action": "Submitted W-9 for Vendor A", "status": "ok", "ref": "SUBM-2025-0912-XYZ"},
            {"time": "09:15", "agent": "Compliance Checker", "action": "Flagged missing DP addendum", "status": "flagged", "ref": "Vendor_A_Master_Agreement.pdf"},
            {"time": "08:44", "agent": "Audit Prep", "action": "Pack compiled for Aug", "status": "ok", "ref": "audit_pack_2025-08.zip"},
        ]

    for item in feed:
        color = {"ok": "#16a34a", "flagged": "#ef4444", "in-progress": "#f59e0b"}.get(item.get("status", "ok"), "#6b7280")
        st.markdown(
            f"""
            <div style="border-bottom:1px solid #f1f5f9;padding:10px 2px;">
                <span style="font-size:12px;color:#6b7280;">{item.get('time','')}</span>
                <span style="margin:0 8px;">{status_dot(color)}</span>
                <strong>{item.get('agent','')}</strong>
                <span style="color:#111827;">— {item.get('action','')}</span>
                <span style="font-size:12px;color:#6b7280;margin-left:8px;">{item.get('ref','')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption("Tip: Place images in ./assets/agents (or keep the demo fallbacks). Wire real functions in services.agents when ready.")
