import streamlit as st
from services.store import load_slack_digest, load_tasks, load_people
from services.agents import summarize_standups, list_prs_needing_attention, prep_one_on_one

st.title("Agents – Utilities")

digest = load_slack_digest()
tasks = load_tasks()
people = load_people()

st.subheader("Stand-up Summarizer")
if st.button("Summarize last 24h"):
    summary = summarize_standups(digest)
    st.markdown("**Wins**")
    for w in summary.get("wins", []): st.markdown(f"- {w}")
    st.markdown("**Risks**")
    for r in summary.get("risks", []): st.markdown(f"- {r}")
    st.markdown("**Next Steps**")
    for n in summary.get("next", []): st.markdown(f"- {n}")

st.subheader("PRs Needing Attention")
prs = list_prs_needing_attention(tasks)
for pr in prs:
    st.markdown(f"- PR #{pr['id']}: {pr['title']} (age: {pr['age_days']} days)")

st.subheader("Prep a 1:1")
names = {p['name']: p for p in people}
name = st.selectbox("Select report", list(names.keys()))
if st.button("Prepare 1:1 agenda"):
    agenda = prep_one_on_one(names[name], digest, company="mentorvista")
    st.markdown("**Agenda**")
    for a in agenda.get("agenda", []): st.markdown(f"- {a}")
    st.markdown("**Growth Topic**\n- " + agenda.get("growth_topic", ""))
    st.markdown("**Policy Citations**")
    for c in agenda.get("policy_citations", []):
        st.markdown(f"- **[{c['doc']} › {c['section']}]** — {c['excerpt']}")
