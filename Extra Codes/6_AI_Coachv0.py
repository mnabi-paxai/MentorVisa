# pages/6_AI_Coach.py
import os
import time
import pathlib
import streamlit as st

from services.policy_loader import load_policy_dir
from services.policy_index import PolicyIndex, PolicyHit
from services.coach_ai import VistaCoach

st.set_page_config(page_title="AI Coach (Policy-Aware)", page_icon="🧭", layout="wide")

# ---------- Sidebar: model + key + strict mode ----------
with st.sidebar:
    st.header("AI Settings")
    model = st.selectbox(
        "OpenAI model",
        options=[
            "gpt-4o-mini",
            "gpt-4o",
            "o3-mini-high",
        ],
        index=0,
        help="Pick a lightweight or stronger model depending on cost/latency."
    )
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Stored only in this session (not written to disk)."
    )
    strict_mode = st.toggle(
        "Strict policy mode",
        value=False,
        help="If ON, responses must include a relevant policy reference or the coach will decline."
    )
    st.caption("Policies are read from `./data/policies`. Replace with your own.")
    st.divider()
    temperature = st.slider("Creativity (temperature)", 0.0, 1.2, 0.4, 0.1)

# ---------- Page Header ----------
st.title("🧭 AI Coach (Policy-Aware)")
st.caption("Personalized leadership guidance grounded in your company policies.")

# ---------- Build / cache policy index ----------
@st.cache_resource(show_spinner=True)
def _get_policy_index() -> PolicyIndex:
    data_dir = pathlib.Path("./data/policies").resolve()
    chunks = load_policy_dir(str(data_dir))
    idx = PolicyIndex()
    if chunks:
        idx.build(chunks)
    return idx

idx = _get_policy_index()
st.info(f"Policy corpus loaded: {idx.size} chunks • source: `./data/policies`")

# ---------- Initialize the coach + chat memory ----------
if "vista" not in st.session_state:
    st.session_state.vista = None

if "chat" not in st.session_state:
    st.session_state.chat = []  # list of {"role": "user"|"assistant", "content": "...", "grounding": [...]}

if api_key:
    st.session_state.vista = VistaCoach(api_key=api_key, model=model, temperature=temperature, index=_get_policy_index())

# ---------- Input area ----------
col_in, col_meta = st.columns([5, 3], gap="large")

with col_in:
    prompt = st.chat_input("Ask Vista about a real situation (e.g., 'How do I give constructive feedback?').")
    # Render conversation
    # Render conversation (newest first) — this must be executable Python, not a string
    for turn in reversed(st.session_state.chat):
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            # Show grounding if present
            if turn.get("grounding"):
                with st.expander("Grounding (policy references)"):
                    for g in turn["grounding"]:
                        st.markdown(f"- **{g['doc_id']} › {g['section']}** — score: {g['score']:.2f}")
                        st.caption(g["text"])

    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if not api_key:
            with st.chat_message("assistant"):
                st.error("Please enter an OpenAI API key in the sidebar to use the AI Coach.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    answer, hits = st.session_state.vista.coach(
                        user_input=prompt,
                        history=[(t["role"], t["content"]) for t in st.session_state.chat],
                        strict_policy=strict_mode,
                    )
                    st.write(answer)
                    if hits:
                        with st.expander("Grounding (policy references)"):
                            for h in hits:
                                st.markdown(f"- **{h.meta['doc_id']} › {h.meta['section']}** — score: {h.score:.2f}")
                                st.caption(h.text)
                    st.session_state.chat.append({
                        "role": "assistant",
                        "content": answer,
                        "grounding": [
                            {"doc_id": h.meta["doc_id"], "section": h.meta["section"], "score": h.score, "text": h.text}
                            for h in (hits or [])
                        ]
                    })

with col_meta:
    st.subheader("How it works")
    st.markdown(
        """
- Searches your **company policies** first.
- If a relevant section exists, it **feeds that context** into the LLM and drafts a polished response.
- If **no matching policy** is found, it clearly says so and answers using leadership best practices.
- Toggle **Strict policy mode** to require a policy reference (otherwise it will decline).
- Keeps a **back-and-forth** chat history.
        """
    )
