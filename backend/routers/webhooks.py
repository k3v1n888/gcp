from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager

router = APIRouter()

@router.post("/api/webhooks/wazuh")
async def handle_wazuh_webhook(request: Request, db: Session = Depends(database.get_db)):
    """
    Receives real-time alerts from the Wazuh integrator via a webhook,
    processes them, and saves them to the database.
    """
    alert_json = await request.json()
    
    rule = alert_json.get("rule", {})
    agent = alert_json.get("agent", {})
    
    rule_desc = rule.get("description", "Wazuh Alert")
    agent_ip = agent.get("ip", "N/A")

    severity = "high"
    if rule.get("level", 0) >= 12:
        severity = "critical"

    db_log = models.ThreatLog(
        ip=agent_ip,
        threat=rule_desc,
        source="Quantum XDR (Wazuh)",
        severity=severity,
        tenant_id=1,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())

    return {"status": "success", "ingested_alert_id": db_log.id}