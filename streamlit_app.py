import streamlit as st

st.set_page_config(page_title="MentorVista", layout="wide")

st.title("MentorVista – AI Coaching & Ops Dashboard")
st.caption("Policy-grounded coaching, tailored to your team and your work context.")

st.markdown("""
**Welcome!** Use the sidebar to navigate:

- **Coach** – Policy-aware AI coaching with inline citations.
- **People** – Team profiles.
- **Tasks** – Admin automation, approvals, KPIs, and follow-ups.
- **Agents** – AI agents.
""")
