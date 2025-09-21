# MentorVista – AI Coaching & Ops Dashboard (MVP)

Policy-grounded coaching for managers with an operations dashboard and simple agents. This MVP ships with **local mock data** and a **policy retrieval** layer so all advice cites relevant HR policy snippets.

## Quickstart

```bash
# 1) Create & activate a virtual environment (optional but recommended)
python -m venv .venv
source ./.venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
streamlit run streamlit_app.py
```

Open the Streamlit sidebar to navigate between pages.

## Project Structure
```
MentorVista/
  ├─ streamlit_app.py        # Home page
  ├─ pages/
  │   ├─ 1_Coach.py
  │   ├─ 2_People.py
  │   ├─ 3_Tasks.py
  │   ├─ 4_Dashboard.py
  │   └─ 5_Agents.py
  ├─ services/
  │   ├─ coach.py
  │   ├─ policy_index.py
  │   ├─ store.py
  │   ├─ agents.py
  │   └─ connectors.py
  ├─ utils/
  │   ├─ prompts.py
  │   └─ ui.py
  ├─ data/
  │   ├─ people.json
  │   ├─ tasks.json
  │   ├─ slack_digest.json
  │   ├─ github_mock.json
  │   └─ policies/
  │       ├─ mentorvista_perf_mgmt.md
  │       └─ mentorvista_timeoff.md
  ├─ .streamlit/
  │   ├─ config.toml
  │   └─ secrets.toml  # (template)
  └─ requirements.txt
```

## Policy Grounding

- Policies are stored as markdown in `data/policies/` and indexed locally with TF‑IDF.
- The Coach cites the top relevant snippets with **[doc_id › section]** style.
- Toggle **Strict policy mode** on the Coach page to refuse actions without a matching policy reference.

## Mock Integrations

- Slack and GitHub data are mocked via JSON files in `data/`. Replace with real connectors later.
- See `services/connectors.py` for placeholders and feature flags.

## Notes
- This scaffold avoids external writes (no posting back to Slack/GitHub).
- Keep actual company policies private; replace the demo docs with your own and re-run.
