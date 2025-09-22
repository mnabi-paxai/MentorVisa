# pages/6_AI_Coach.py
import pathlib
import streamlit as st

from services.policy_loader import load_policy_dir
from services.policy_index import PolicyIndex
from services.coach_ai import VistaCoach

st.set_page_config(page_title="AI Coach (Policy-Aware)", page_icon="🧭", layout="wide")

# =========================
# Sidebar: Model + API Key
# =========================
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
        help="Used only in this session; not written to disk."
    )
    strict_mode = st.toggle(
        "Strict policy mode",
        value=False,
        help="If ON, the coach will only answer when a relevant policy snippet is found."
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.2, 0.4, 0.1)
    st.caption("Policies are loaded from `./data/policies`.")

# =========================
# Header
# =========================
st.title("🧭 AI Coach (Policy-Aware)")
st.caption("Personalized leadership guidance grounded in your company policies.")

# =========================
# Build / cache policy index
# =========================
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

# =========================
# Session state
# =========================
if "vista" not in st.session_state:
    st.session_state.vista = None

if "chat" not in st.session_state:
    st.session_state.chat = []  # list of dicts: {"role": "user"|"assistant", "content": str, "grounding": [...]}

# Initialize Vista coach if key is present
if api_key:
    st.session_state.vista = VistaCoach(
        api_key=api_key,
        model=model,
        temperature=temperature,
        index=idx,
    )

# =========================
# Layout: widen chat column
# =========================
col_in, col_meta = st.columns([7, 2], gap="large")

with col_in:
    # -------------------------
    # Chat input (top of page)
    # -------------------------
    prompt = st.chat_input("Ask Vista about a real situation (e.g., 'How do I give constructive feedback?').")

    # -----------------------------------------------------
    # Handle a new turn atomically, then force a clean rerun
    # -----------------------------------------------------
    if prompt:
        # 1) append user turn
        st.session_state.chat.append({"role": "user", "content": prompt})

        # 2) produce assistant turn (no partial rendering here)
        if not api_key:
            st.session_state.chat.append({
                "role": "assistant",
                "content": "Please enter an OpenAI API key in the left sidebar to use the AI Coach.",
            })
        else:
            answer, hits = st.session_state.vista.coach(
                user_input=prompt,
                history=[(t["role"], t["content"]) for t in st.session_state.chat],
                strict_policy=strict_mode,
            )
            st.session_state.chat.append({
                "role": "assistant",
                "content": answer,
                "grounding": [
                    {
                        "doc_id": getattr(h.meta, "get", lambda *_: None)("doc_id") if isinstance(h.meta, dict) else "",
                        "section": h.meta.get("section", "") if isinstance(h.meta, dict) else "",
                        "score": h.score,
                        "text": h.text
                    }
                    for h in (hits or [])
                ],
            })

        # 3) redraw once so ordering is correct (newest at top)
        st.rerun()

    # ---------------------------------------
    # Render the entire conversation ONCE
    # newest first (top), oldest last (bottom)
    # ---------------------------------------
    for turn in reversed(st.session_state.chat):
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            if turn.get("grounding"):
                with st.expander("Grounding (policy references)"):
                    for g in turn["grounding"]:
                        doc = g.get("doc_id", "")
                        sec = g.get("section", "")
                        sc = g.get("score", 0.0)
                        st.markdown(f"- **{doc} › {sec}** — score: {sc:.2f}")
                        st.caption(g.get("text", ""))

with col_meta:
    st.subheader("How it works")
    st.markdown(
        """
- Searches your **company policies** first.
- If relevant sections exist, they are fed as **context** and shown as **Grounding (policy references)**.
- If **no matching policy** is found, Vista either (a) declines in **Strict mode**, or (b) clearly says so and provides best-practice guidance.
- Conversation is kept **newest at the top**.
        """
    )
