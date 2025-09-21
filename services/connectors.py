"""Placeholders for future Slack/GitHub connectors.

Set feature flags and token retrieval here. Keep read-only for MVP.
"""
import os

USE_REAL_SLACK = os.getenv("MV_USE_REAL_SLACK", "0") == "1"
USE_REAL_GITHUB = os.getenv("MV_USE_REAL_GITHUB", "0") == "1"

def fetch_slack_digest():
    if not USE_REAL_SLACK:
        return None  # handled by store.load_slack_digest()
    # TODO: implement Slack Web API read wrapper
    raise NotImplementedError("Slack connector not implemented in MVP.")

def fetch_github_prs():
    if not USE_REAL_GITHUB:
        return None
    # TODO: implement GitHub REST read wrapper
    raise NotImplementedError("GitHub connector not implemented in MVP.")
