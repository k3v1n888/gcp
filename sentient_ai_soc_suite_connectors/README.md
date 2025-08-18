
# Sentient AI-SOC Suite (Monorepo)

This is a **plug-and-play** scaffold to integrate your own AI model across three layers:
1) **Ingest** (AI Router + Auto-Mapper) → CanonicalEvent + FeatureVector
2) **Threat Service** (uses YOUR model via `REMOTE_MODEL_URL`)
3) **Policy Service** (turns detections into action plans)
4) **Orchestrator** (chains the flow)

## Run locally (4 terminals)
### Ingest (port 8000)
cd services/ingest && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app:app --reload --port 8000

### Threat (port 8001)
cd services/threat_service && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app:app --reload --port 8001
# Optional: export REMOTE_MODEL_URL=http://localhost:9000/predict  # your own model API

### Policy (port 8002)
cd services/policy_service && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app:app --reload --port 8002

### Orchestrator (port 8003)
cd services/orchestrator && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app:app --reload --port 8003

## End-to-end test
curl -s -X POST "http://localhost:8003/events/ingest" -H "Content-Type: application/json" -d @services/ingest/tests/samples/wazuh_sample.json | jq

## Plug in YOUR model
Set `REMOTE_MODEL_URL` in **threat_service** to your model endpoint that accepts:
{"features": FeatureVector}
and returns:
{"severity":"high","confidence":0.83,"findings":["SQLi"], "shap":{"feature":"value"}}

Or modify `services/threat_service/model/loader.py` to load your local model.

## Notes
- All services use **shared/schemas.py** for strict contracts.
- Policy decisions are in **policy_service/policy.yaml**.
- Add new mappings under **ingest/mappings**.


## Web Console (mapping approvals)
Service at **services/console** (port 8005)
```
cd services/console
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8005
```
- Visit http://localhost:8005 to list mappings and paste a proposed YAML to approve.

## Connectors (Slack/Teams/Jira) via Orchestrator
Set env vars before running orchestrator:
```
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="you@your-domain.com"
export JIRA_API_TOKEN="your_api_token"
export JIRA_PROJECT_KEY="SEC"
```
Execute actions from a policy plan:
```
curl -s -X POST http://localhost:8003/actions/execute  -H "Content-Type: application/json"  -d '{"action_plan":[{"action":"notify","channel":"#soc","priority":"p1"},{"action":"ticket","template":"high-incident"}], "options":{"notify_via":"slack","jira_issue_type":"Task","dry_run":false}}' | jq
```
