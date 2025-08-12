
import yaml
from fastapi import FastAPI, Body
from typing import List
from shared.schemas import PolicyRequest, PolicyResponse, ActionItem

app = FastAPI(title="Policy Service", version="0.1.0")

with open("policy.yaml","r") as f:
    POLICY = yaml.safe_load(f)

@app.get("/health")
def health(): return {"ok": True}

def decide(req: PolicyRequest) -> PolicyResponse:
    defaults = POLICY.get("defaults",{})
    plan: List[ActionItem] = []
    for rule in POLICY.get("rules",[]):
        cond = rule.get("when",{})
        if cond.get("severity") == req.severity:
            for step in rule.get("plan",[]):
                d = {**defaults, **step}
                plan.append(ActionItem(**d))
            break
    rollbacks = []
    for s in plan:
        if s.action == "contain" and s.type == "block-ip":
            rollbacks.append(ActionItem(action="unblock-ip", target=s.target, value=s.value))
    explain = f"Policy decided {len(plan)} actions for severity={req.severity}, confidence={req.confidence:.2f}"
    return PolicyResponse(action_plan=plan, rollbacks=rollbacks, explain=explain)

@app.post("/policy/decide", response_model=PolicyResponse)
def policy_decide(req: PolicyRequest = Body(...)):
    return decide(req)
