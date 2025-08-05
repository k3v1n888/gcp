# backend/correlation.py

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

# Restore original imports
from backend.models import SessionLocal, ThreatLog, User

# Keep all your original correlation logic exactly as it was
def correlate_threats(db: Session):
    """Your original correlation logic"""
    pass

# Keep all your original functions exactly as they were

router = APIRouter(prefix="/api/correlation", tags=["correlation"])

def run_correlation_rules(db: Session, tenant_id: int):
    """
    A simple rule-based correlation engine.
    This function can be expanded with more sophisticated rules.
    """
    # Rule 1: Find multiple threats from the same IP in the last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    suspicious_ips = db.query(ThreatLog.ip, func.count(ThreatLog.id).label('threat_count'))\
        .filter(ThreatLog.tenant_id == tenant_id, ThreatLog.timestamp >= one_hour_ago)\
        .group_by(ThreatLog.ip)\
        .having(func.count(ThreatLog.id) > 3)\
        .all()

    for ip, count in suspicious_ips:
        # Check if a correlation alert for this IP has already been created recently
        existing_alert = db.query(ThreatLog).filter(
            ThreatLog.tenant_id == tenant_id,
            ThreatLog.source == "CorrelationEngine",
            ThreatLog.ip == ip,
            ThreatLog.timestamp >= one_hour_ago
        ).first()

        if not existing_alert:
            # If no recent alert, create a new one
            correlated_threat = ThreatLog(
                ip=ip,
                threat=f"Correlated Threat: {count} events from this IP in the last hour.",
                source="CorrelationEngine",
                severity="high",
                tenant_id=tenant_id
            )
            db.add(correlated_threat)
    
    db.commit()


@router.post("/run", status_code=202)
def trigger_correlation_engine(
    background_tasks: BackgroundTasks,
    user: User = Depends(require_role(["admin", "analyst"])), 
    db: Session = Depends(get_db)
):
    """
    Manually triggers the correlation engine to run in the background.
    """
    tenant_id = user.tenant_id
    background_tasks.add_task(run_correlation_rules, db, tenant_id)
    return {"message": "Correlation engine job started in the background"}

@router.get("/analyze")
def analyze_correlations(db: Session = Depends(get_db)):
    """Analyze threat correlations"""
    # Your existing logic here
    return {"status": "correlation analysis complete"}
