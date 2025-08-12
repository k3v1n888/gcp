import os, json, base64, requests
from typing import Dict, Any, List

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SEC")

def notify_slack(text: str, channel: str | None = None):
    if not SLACK_WEBHOOK_URL:
        return {"ok": False, "error": "SLACK_WEBHOOK_URL not set"}
    payload = {"text": text}
    if channel: payload["channel"] = channel  # works when webhook is for app/bot; for simple incoming hooks channel may be fixed
    r = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    return {"ok": r.status_code in (200, 204), "status": r.status_code, "resp": r.text}

def notify_teams(text: str):
    if not TEAMS_WEBHOOK_URL:
        return {"ok": False, "error": "TEAMS_WEBHOOK_URL not set"}
    card = {
      "@type": "MessageCard",
      "@context": "http://schema.org/extensions",
      "summary": "CXyber Notification",
      "text": text
    }
    r = requests.post(TEAMS_WEBHOOK_URL, json=card, timeout=10)
    return {"ok": r.status_code in (200, 204), "status": r.status_code, "resp": r.text}

def create_jira_ticket(summary: str, description: str, issue_type: str = "Task"):
    if not (JIRA_BASE_URL and JIRA_EMAIL and JIRA_API_TOKEN and JIRA_PROJECT_KEY):
        return {"ok": False, "error": "Jira env vars not set (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY)"}
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    payload = {
      "fields": {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": summary,
        "description": description,
        "issuetype": {"name": issue_type}
      }
    }
    headers = {"Accept":"application/json", "Content-Type":"application/json"}
    r = requests.post(url, auth=auth, headers=headers, json=payload, timeout=15)
    ok = r.status_code in (200, 201)
    data = r.json() if ok else {"error": r.text}
    return {"ok": ok, "status": r.status_code, "data": data}
