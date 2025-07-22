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
    
    # Extract relevant data from the Wazuh alert structure
    rule = alert_json.get("rule", {})
    agent = alert_json.get("agent", {})
    
    rule_desc = rule.get("description", "Wazuh Alert")
    agent_ip = agent.get("ip", "N/A")

    # For this webhook, we can assume a high severity
    severity = "high"
    if rule.get("level", 0) >= 12:
        severity = "critical"

    # Save the new alert to your database
    db_log = models.ThreatLog(
        ip=agent_ip,
        threat=rule_desc,
        source="Quantum XDR (Wazuh)",
        severity=severity,
        tenant_id=1, # Defaulting to tenant 1 for system alerts
        timestamp=datetime.now(timezone.utc)
        # ip_reputation_score and cve_id can be added later via enrichment
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Broadcast the new log to the dashboard
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())

    return {"status": "success", "ingested_alert_id": db_log.id}