# pages/1_Coach.py
import streamlit as st
from services.coach import get_coaching, IDX   # IDX is the singleton index in coach.py
from services.policy_loader import load_policy_dir

# Must be first Streamlit call
st.set_page_config(page_title="MentorVista Coach", page_icon="🧭")

# ---------- Build policy index once ----------
@st.cache_resource(show_spinner=False)
def _build_policy_index() -> int:
    chunks = load_policy_dir("./data/policies")
    if chunks:
        IDX.build(chunks)
    return len(chunks)

num_chunks = _build_policy_index()
st.caption(f"📚 Policy corpus loaded: {num_chunks} chunks")

# Optional: reload while iterating on policy files
with st.sidebar:
    st.header("MentorVista • Coach")
    if st.button("🔄 Reload policies"):
        _build_policy_index.clear()   # clear cache
        n = _build_policy_index()
        st.toast(f"Reloaded {n} policy chunks.")

# ---------- UI ----------
st.title("🧭 MentorVista Coach")

# State
st.session_state.setdefault("history", [])
st.session_state.setdefault("last_advice", None)

# Inputs
persona = st.selectbox("Who’s involved?", ["General", "Direct report", "Peer", "Manager", "Executive", "HR"])
company = st.text_input("Company (optional)", value="")
target = st.selectbox("Coaching goal", ["Clarity", "Decision", "Feedback", "Conflict", "Career", "Other"])
strict = st.checkbox("Strictly follow company HR policy grounding (stricter match)", value=True)
msg = st.text_area("Describe the situation", placeholder="What happened? What do you want to achieve?")

# Action
advice = None
if st.button("Get Coaching") and msg.strip():
    try:
        advice = get_coaching(
            msg, persona=persona, target=target, company=company, strict=strict
        )
        st.session_state.last_advice = advice
        st.session_state.history.append({"you": msg, "coach": advice})
    except Exception as e:
        st.error(f"Failed to get coaching: {e}")

# If no new advice this run, reuse the last
if advice is None:
    advice = st.session_state.last_advice

# ---------- Output (guarded) ----------
if advice:
    badge = (
        "✅ Grounded in company policy"
        if advice.get("grounding") == "policy"
        else "ℹ️ General coaching (no matching policy found)"
    )
    st.caption(badge)

    st.success(advice.get("quick_take", ""))

    if advice.get("reasoning"):
        with st.expander("Why this advice"):
            st.write(advice["reasoning"])

    if advice.get("steps"):
        st.subheader("Suggested next steps")
        for i, step in enumerate(advice["steps"], 1):
            st.write(f"{i}. {step}")

    if advice.get("policy_refs"):
        with st.expander("Policy references"):
            for ref in advice["policy_refs"]:
                src = ref.get("source_title") or ref.get("source") or "policy"
                sec = ref.get("section") or "—"
                sc = ref.get("score")
                st.write(f"- {src} §{sec} (score={sc})")

    # Debug helper while tuning retrieval threshold
    if st.checkbox("Show retrieval debug"):
        st.json(advice.get("debug", {}))

# ---------- History ----------
if st.session_state.history:
    st.divider()
    st.caption("Conversation history")
    for turn in reversed(st.session_state.history[-10:]):
        st.markdown(f"**You:** {turn['you']}")
        coach = turn.get("coach") or {}
        qt = coach.get("quick_take", "")
        if qt:
            st.markdown(f"**Coach:** {qt}")
