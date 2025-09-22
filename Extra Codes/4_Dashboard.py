import streamlit as st
from services.store import load_slack_digest, load_tasks

st.title("Dashboard – Signals & Trends (Mock)")

digest = load_slack_digest()
tasks = load_tasks()

col1, col2, col3 = st.columns(3)
with col1:
    total_msgs = sum(c['messages_24h'] for c in digest.get('channels', []))
    st.metric("Slack messages (24h)", total_msgs)
with col2:
    unreplied = sum(c['unreplied_asks'] for c in digest.get('channels', []))
    st.metric("Unreplied asks", unreplied)
with col3:
    prs = len(tasks.get("prs", []))
    st.metric("PRs awaiting review", prs)

st.subheader("Channel Signals")
for ch in digest.get("channels", []):
    st.markdown(f"- **{ch['name']}** – msgs: {ch['messages_24h']}, unreplied: {ch['unreplied_asks']}, after-hours: {ch['after_hours_pct']}%  ")
    st.markdown(f"  Theme: _{ch['top_theme']}_")

st.subheader("Top Risks")
for r in digest.get("risks", []):
    st.markdown(f"- {r}")
