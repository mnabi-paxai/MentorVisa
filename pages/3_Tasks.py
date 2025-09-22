# pages/3_Tasks.py
import uuid
from datetime import datetime
import streamlit as st

# --- Data hooks (existing) ---
from services.store import load_tasks  # returns dict with {approvals, prs, followups, ...}
from services.agents import draft_followup  # used for PR follow-up messages

# ---------------------------------------------------------
# Page
# ---------------------------------------------------------
st.set_page_config(page_title="Tasks", page_icon="🗂️", layout="wide")
st.title("Tasks")

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _load_kpis():
    """
    Wire to your real KPI source later (e.g., services.store.load_kpis()).
    Fallback ensures the page always renders.
    Expected shape:
      [{"name": str, "value": float|int, "target": float|int, "delta": float|int, "unit": "%"|"" , "series": [..]}]
    """
    try:
        # from services.store import load_kpis
        # return load_kpis()
        raise ImportError
    except Exception:
        return [
            {"name": "On-time Delivery", "value": 0.72, "target": 0.85, "delta": -0.06, "unit": "%", "series": [0.81, 0.79, 0.78, 0.72]},
            {"name": "NPS", "value": 41, "target": 50, "delta": 3, "unit": "", "series": [36, 38, 39, 41]},
            {"name": "Open Headcount", "value": 3, "target": 0, "delta": 0, "unit": "", "series": [5, 4, 3, 3]},
        ]

def _fmt_pct(x):
    return f"{x*100:.0f}%" if isinstance(x, float) else f"{x}%"

def _delta_chip(delta, suffix=""):
    if delta is None:
        return ""
    sign = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
    return f"{sign} {abs(delta)*100:.0f}%{suffix}" if isinstance(delta, float) else f"{sign} {abs(delta)}{suffix}"

def _tiny_spark(series):
    # minimalist sparkline; auto-sizes to the container
    st.line_chart(series, height=60, use_container_width=True)

def _task_row(title, meta, due=None, actions=None):
    with st.container(border=True):
        left, right = st.columns([0.75, 0.25])
        with left:
            due_str = f" · Due: {due}" if due else ""
            st.markdown(
                f"**{title}**  \n"
                f"<small style='opacity:0.7'>{meta}{due_str}</small>",
                unsafe_allow_html=True,
            )
        with right:
            if actions:
                cols = st.columns(len(actions))
                for i, (label, key, on_click) in enumerate(actions):
                    if cols[i].button(label, key=key):
                        on_click()

def _due_str(d):
    return d or "—"

# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
tasks_data = load_tasks() or {}
approvals = tasks_data.get("approvals", [])
prs = tasks_data.get("prs", [])
followups = tasks_data.get("followups", [])

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
tab_kpi, tab_inbox, tab_autom = st.tabs(["KPI", "Universal Inbox", "Approvals & Automations"])

# =========================
# Tab 1: KPI
# =========================
with tab_kpi:
    st.subheader("KPI Snapshot")
    kpis = _load_kpis()

    cols = st.columns(min(4, max(1, len(kpis))))
    for i, k in enumerate(kpis):
        with cols[i % len(cols)]:
            # metric tile
            if k.get("unit") == "%":
                current_val = _fmt_pct(k["value"])
                target_val = _fmt_pct(k["target"])
                delta_str = _delta_chip(k.get("delta"), suffix="")
            else:
                current_val = f"{k['value']}"
                target_val = f"{k['target']}"
                d = k.get("delta", 0)
                delta_str = f"{'↑' if d > 0 else ('↓' if d < 0 else '→')} {abs(d)}"

            st.metric(k["name"], current_val, delta_str, help=f"Target: {target_val}")
            _tiny_spark(k.get("series", []))

# =========================
# Tab 2: Universal Inbox
# =========================
with tab_inbox:
    st.subheader("Universal Inbox")
    view = st.segmented_control("View", ["Today", "This Week", "Approvals", "Waiting"], default="Today")

    # Approvals slice
    if view in ("Today", "This Week", "Approvals"):
        st.caption("Approvals")
        if approvals:
            for ap in approvals:
                def _approve_closure(a=ap):
                    def _run():
                        st.success(f"Approved: {a.get('title')}  •  Audit ID: {uuid.uuid4().hex[:8].upper()}")
                    return _run

                _task_row(
                    title=ap.get("title", "Approval"),
                    meta=f"{ap.get('system','HRIS/Finance')} — status: {ap.get('status','pending')}",
                    due=_due_str(ap.get("due")),
                    actions=[
                        ("Approve", f"appr_{ap.get('id',uuid.uuid4().hex)}", _approve_closure()),
                        ("Open", f"open_{ap.get('id',uuid.uuid4().hex)}", lambda url=ap.get("url", "#"): st.toast(f"Open: {url}")),
                    ],
                )
        else:
            st.info("No approvals right now.")

    # PRs slice
    if view in ("Today", "This Week"):
        st.caption("PRs Needing Attention")
        if prs:
            for pr in prs:
                def _followup_closure(p=pr):
                    def _run():
                        msg = draft_followup(
                            {"type": "pr", "id": p.get("id"), "title": p.get("title"), "age_days": p.get("age_days")}
                        )
                        st.code(msg or "*No draft generated.*", language="markdown")
                    return _run

                _task_row(
                    title=f"PR #{pr.get('id')}: {pr.get('title','')}",
                    meta=f"GitHub — status: {pr.get('status','open')} — age: {pr.get('age_days','?')}d",
                    due=None,
                    actions=[
                        ("Draft Follow-up", f"fu_{pr.get('id',uuid.uuid4().hex)}", _followup_closure()),
                        ("Open", f"open_pr_{pr.get('id',uuid.uuid4().hex)}", lambda url=pr.get("url", "#"): st.toast(f"Open: {url}")),
                    ],
                )
        else:
            st.info("No PRs waiting on you.")

    # Other follow-ups slice
    if view in ("Today", "This Week", "Waiting"):
        st.caption("Other Follow-ups")
        if followups:
            for fu in followups:
                _task_row(
                    title=fu.get("title", "Follow-up"),
                    meta=f"Owner: {fu.get('owner','—')}",
                    due=_due_str(fu.get("due")),
                    actions=[
                        ("Complete", f"done_{fu.get('id',uuid.uuid4().hex)}", lambda: st.success("Marked complete")),
                        ("Open", f"open_fu_{fu.get('id',uuid.uuid4().hex)}", lambda url=fu.get("url", "#"): st.toast(f"Open: {url}")),
                    ],
                )
        else:
            st.info("Nothing else on your plate.")

# =========================
# Tab 3: Approvals & Automations
# =========================
with tab_autom:
    st.subheader("Run an Automation")
    st.caption("Natural language → dry-run preview → confirm → execute (with audit log).")

    examples = [
        "Approve PTO for Ava Chen from Oct 7–10",
        "Submit expense report for NYC trip (Aug 12–15) in Brex",
        "Create a Jira bug: Login loop on mobile, assign to SRE",
        "Schedule 30m 1:1s with my 3 new hires next week",
    ]
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        user_cmd = st.text_input("Type a command", placeholder=examples[0])
    with c2:
        ex = st.selectbox("Examples", options=examples, index=0, label_visibility="collapsed")
        if st.button("Use Example"):
            st.session_state["__cmd_prefill__"] = ex
            st.experimental_rerun()

    # Simple NL → plan (stub; swap with MCP routing)
    plan = None
    raw_cmd = st.session_state.get("__cmd_prefill__") or user_cmd
    if raw_cmd:
        lower = raw_cmd.lower()
        if "pto" in lower:
            plan = "System: BambooHR\nAction: approve_pto(employee='Ava Chen', start='2025-10-07', end='2025-10-10')"
        elif any(k in lower for k in ("expense", "brex", "ramp", "concur")):
            plan = "System: Brex\nAction: submit_expense(report='NYC trip Aug 12–15', category='Travel')"
        elif "jira" in lower:
            plan = "System: Jira\nAction: create_issue(type='bug', title='Login loop on mobile', assignee='SRE')"
        elif "schedule" in lower:
            plan = "System: Google Calendar\nAction: schedule(title='1:1', attendees='new hires', duration='30m', window='next week')"
        else:
            plan = "System: Auto\nAction: (attempt to infer best tool & safe parameters)"

    col_a, col_b = st.columns([0.5, 0.5])
    with col_a:
        st.caption("Dry-run")
        if plan:
            st.code(plan, language="yaml")
        else:
            st.info("Enter a command to preview the dry-run plan.")

    with col_b:
        st.caption("Execute")
        if st.button("Run with Confirmation", disabled=(plan is None)):
            audit_id = f"AUD-{uuid.uuid4().hex[:10].upper()}"
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            st.success(f"Executed.\n\n**Audit ID:** {audit_id}\n**When:** {timestamp}\n**Command:** {raw_cmd}")

    st.divider()
    st.caption("Notes")
    st.markdown(
        "- Preview every action before it mutates external systems.\n"
        "- Log executions with an Audit ID.\n"
        "- Validate permissions per integration (read-only vs write)."
    )
