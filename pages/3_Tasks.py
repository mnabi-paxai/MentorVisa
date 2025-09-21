import streamlit as st
from services.store import load_tasks
from services.agents import draft_followup

st.title("Tasks – Approvals, PRs, Follow-ups")

data = load_tasks()

st.subheader("Approvals")
for ap in data.get("approvals", []):
    st.markdown(f"- **{ap['title']}** (due {ap['due']}) — status: {ap['status']}")

st.subheader("PRs Needing Attention")
for pr in data.get("prs", []):
    st.markdown(f"- PR #{pr['id']}: {pr['title']} (age: {pr['age_days']} days) – status: {pr['status']}")
    if st.button(f"Draft follow-up for PR #{pr['id']}", key=f"pr_{pr['id']}"):
        msg = draft_followup({"type": "pr", "id": pr['id'], "title": pr['title'], "age_days": pr['age_days']})
        st.code(msg, language="markdown")

st.subheader("Other Follow-ups")
for fu in data.get("followups", []):
    st.markdown(f"- **{fu['title']}** (owner: {fu['owner']}, due: {fu['due']})")
