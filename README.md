# MentorVista – AI Coaching & Ops Dashboard (MVP)

MentorVista is an AI-first leadership operating system for middle managers, grounded in company policies and compliant with top data privacy and security standards. It delivers real-time coaching, team and task visibility, and automation to help managers resolve challenges and drive performance with always-on, personalized support.

## Investment Memo


[View the document on Google Drive](https://drive.google.com/drive/folders/1sQG7epXyBiepEbmqmlICsUXoJRvYasJj?usp=sharing)


<!--
[View the document on Docsend](https://docsend.com/v/n2rzg/mentorvista)

[View the document on Docsend](https://docsend.com/view/hztcxxdqj5rzukw5)

File is available here: [MentorVista Investment Memo](https://drive.google.com/drive/folders/1sQG7epXyBiepEbmqmlICsUXoJRvYasJj?usp=sharing)

<iframe src="https://docsend.com/view/ehzrt4xs3p63c5ip" allow="fullscreen" width="640" height="480"></iframe>


-->

<img src="./assets/summary_image.png" alt="Summary of MentorVista" width="600"/>

<!--
![Alt text](./assets/summary_image.png)
-->

## MentorVista's Vision
MentorVista’s vision is to become the world’s Leadership Engine, the operating system for managers that combines AI coaching, execution support, and predictive insights to transform leadership development and human capital strategy at scale.

## Quickstart

```bash
# 1) Clone the repo 
git clone https://github.com/your-org/MentorVista.git
cd "address"

# 2) Create & activate a virtual environment (optional but recommended)
python -m venv .venv
source ./.venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt ---- pip install streamlit

# 4) Run the app
streamlit run streamlit_app.py
```

Open the Streamlit sidebar to navigate between pages.

## Project Structure
```
MentorVista/
  ├─ streamlit_app.py        # Home page
  ├─ pages/
  │   ├─ 1_AI_Coach.py
  │   ├─ 2_People.py
  │   ├─ 3_Tasks.py
  │   └─ 4_Agents.py
  ├─ services/
  │   ├─ coach.py
  │   ├─ policy_index.py
  │   ├─ policy_loader.py
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
  │       └─ mentorvista_people_policies.md
  │       └─mentorvista_security_compliance_policies.md
  │
  ├─ .streamlit/
  │   ├─ config.toml
  │   └─ secrets.toml  # (template)
  │─ assets/
  │   ├─ employees
  │   └─ agents
  │
  └─ requirements.txt
```

## Policy Grounding

- Policies are stored as markdown in `data/policies/` and indexed locally with TF‑IDF.
- The Coach cites the top relevant snippets with **[doc_id › section]** style.
- Toggle **Strict policy mode** on the Coach page to refuse actions without a matching policy reference.

## Main MVP - AI Coach
<!--
<img src="./assets/AI_Coach.png" alt="AI Coach" width="600"/>
-->

![AI Coach](./assets/AI_coach.png)

### Matching Questions to Company Policies

- **Representation**  
  Every chunk and your question are turned into **TF-IDF vectors** that capture which words and short phrases (unigrams & bigrams) are important.

- **Similarity**  
  We compute **cosine similarity** between your question and each chunk; higher means more overlap in important terms/phrases.

- **Weighting**  
  Some files (like catalogs) are less actionable, so they get a lower *retrieval weight* (e.g., `0.6`).  
  The final score is:  cosine * weight. 
  You can raise a specific policy’s prominence by setting retrieval_weight: 1.2 (in the file’s front-matter).

- **Top-K + Threshold**  
We take the best few (`top_k=4`) and keep only those above a small `min_score` (`0.08` by default) as **relevant**.  
That keeps noise out of the LLM context. 

### OpenAI Integration 
- **Add OpenAI API keys on AI Coach Page** 

- **Try these examples** 
  - What are company policies on PTO?
  - My team moral is low. What to do?


## Employee Profiles
 A comprehensive digital profile for each team member, summarizing projects, responsibilities, skills, mentorship history, morale, and more, providing managers with a holistic view of their people.

![People Page](./assets/ppl.png)

## Task & Automation Dashboard
A centralized hub for managerial tasks such as approvals (e.g., PTO, expense reports). Integrated with enterprise tools via MCP connectors, the dashboard also enables prompt-driven automation of repetitive workflows, freeing up time for higher-value work.

![Tasks Page](./assets/tasks.png)

## AI Agents 
Visibility and control over digital colleagues. Managers can monitor active/inactive agents, assess performance, delegate tasks, and step in where human intervention is required, ensuring smooth collaboration between human and AI team members.

![AI Agents](./assets/AI_agents.png)


## Notes
- This scaffold avoids external writes (no posting back to Slack/GitHub).
- Keep actual company policies private; replace the demo docs with your own and re-run.
- Slack and GitHub data are mocked via JSON files in `data/`. Replace with real connectors later.
- See `services/connectors.py` for placeholders and feature flags.
