# pages/2_people.py
import streamlit as st
from services.people import (
    list_employees,
    get_employee_by_id,
    employee_summary_card,
    get_projects_for_employee,
    get_okrs_for_employee,
    get_pulse_for_employee,
    get_timeoff_for_employee,
    get_kudos_for_employee,
    get_ai_coaching_tips,
)

st.set_page_config(page_title="People • MentorVista", page_icon="👥", layout="wide")

st.title("👥 People")
st.caption("Unified portfolio dashboards for each employee — everything in one place.")

# ---- Employee Selector ----
employees = list_employees()
if not employees:
    st.info("No employees found.")
    st.stop()

id_to_name = {e["id"]: f'{e["name"]} — {e["role"]}' for e in employees}

with st.sidebar:
    st.header("Team")
    chosen_id = st.radio(
        "Select an employee",
        options=list(id_to_name.keys()),
        format_func=lambda x: id_to_name[x],
        index=0,
    )

emp = get_employee_by_id(chosen_id)

# ---- Overview Top Row (always visible) ----
left, right = st.columns([1.1, 2])
with left:
    # renders image if available, otherwise emoji
    employee_summary_card(emp)

with right:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Morale", f'{emp["morale"]["label"]}', f'{emp["morale"]["delta"]}')
    with k2:
        st.metric("Workload", emp["workload"]["label"], emp["workload"]["delta"])
    with k3:
        st.metric("OKR Progress", f'{emp["okr_progress"]} %')
    with k4:
        st.metric("Tenure", emp["tenure_human"])

st.divider()

# ---- ALL FEATURES COMBINED (no tiering) ----
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Projects", "OKRs & Skills", "Engagement", "Time Off", "Kudos", "AI Coaching"]
)

with tab1:
    st.subheader("📌 Current Projects")
    projects = get_projects_for_employee(emp["id"])
    if projects:
        for p in projects:
            with st.expander(f'• {p["name"]}  ({p["status"]})'):
                st.write(p["summary"])
                st.progress(p["progress"])
                st.caption(f'Last update: {p["last_update"]}')
    else:
        st.write("No active projects.")

    st.subheader("🗒️ Manager Notes (mock)")
    st.write(
        "- Keep weekly 1:1 focused on unblockers.\n"
        "- Pair with a mentor on system design reviews.\n"
        "- Recognize recent on-call improvements in team channel."
    )

with tab2:
    st.subheader("🎯 OKRs")
    okrs = get_okrs_for_employee(emp["id"])
    for okr in okrs:
        st.markdown(f'**{okr["title"]}** — _{okr["owner"]}_')
        st.write(okr["desc"])
        st.progress(okr["progress"])
        st.caption(f'Target: {okr["target"]} • Updated: {okr["updated"]}')
        st.divider()

    st.subheader("🧰 Skills Snapshot (mock)")
    chips = ", ".join(emp["skills"])
    st.write(f"**Primary:** {chips}")
    st.caption("Development areas: stakeholder comms, cross-team planning.")

with tab3:
    st.subheader("💚 Engagement & Well-being")
    pulse = get_pulse_for_employee(emp["id"])
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Pulse (last 30d)", f'{pulse["score"]}/10', f'{pulse["delta"]:+.1f} vs prev')
    with c2:
        st.metric("Collaboration", f'{pulse["collab"]}/10')
    with c3:
        st.metric("Stress", f'{pulse["stress"]}/10')
    st.caption("Values are mock; replace with your survey provider integration.")

with tab4:
    st.subheader("🏖️ Time Off")
    to = get_timeoff_for_employee(emp["id"])
    st.write(f'**Balance:** {to["balance_days"]} days')
    for upcoming in to["upcoming"]:
        st.write(f'- {upcoming["label"]}: {upcoming["start"]} → {upcoming["end"]}')

with tab5:
    st.subheader("🎉 Kudos & Feedback")
    for k in get_kudos_for_employee(emp["id"]):
        st.markdown(f'**{k["from"]}** — _{k["date"]}_')
        st.write(k["message"])
        st.divider()

with tab6:
    st.subheader("🤖 AI Coaching Insights (mocked, rules-based)")
    tips = get_ai_coaching_tips(emp)
    for t in tips["manager_tips"]:
        st.write(f'• {t}')
    st.caption("These are deterministic mock insights (no external API calls).")

    st.markdown("**Suggested Check-in Questions**")
    for q in tips["checkins"]:
        st.write(f'• {q}')

st.caption("All data in this page is mock. Replace service functions with real integrations as needed.")
