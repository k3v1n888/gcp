from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from datetime import datetime, timedelta

def correlate_logs_into_incidents(db: Session):
    """
    Analyzes recent, uncorrelated logs and groups them into incidents based on
    attacker IP and a 24-hour time window.
    """
    print("Running incident correlation service...")
    
    # Find recent threats that are not yet part of any incident
    uncorrelated_logs = db.query(models.ThreatLog)\
        .filter(models.ThreatLog.incidents == None)\
        .order_by(models.ThreatLog.timestamp.asc())\
        .limit(200).all()

    for log in uncorrelated_logs:
        # Look for an existing open incident for this IP in the last 24 hours
        time_window = log.timestamp - timedelta(hours=24)
        
        existing_incident = db.query(models.SecurityIncident)\
            .join(models.ThreatLog, models.SecurityIncident.threat_logs)\
            .filter(
                models.SecurityIncident.status == "open",
                models.ThreatLog.ip == log.ip,
                models.SecurityIncident.end_time > time_window
            ).first()

        if existing_incident:
            # Add this log to the existing incident and update its timeline
            existing_incident.threat_logs.append(log)
            existing_incident.end_time = log.timestamp
            # Escalate severity if the new log is more critical
            if severity_to_numeric(log.severity) > severity_to_numeric(existing_incident.severity):
                existing_incident.severity = log.severity
            print(f"Appended log {log.id} to existing incident {existing_incident.id}")
        else:
            # Create a brand new incident for this log
            new_incident = models.SecurityIncident(
                title=f"Suspicious Activity from {log.ip}",
                status="open",
                severity=log.severity,
                start_time=log.timestamp,
                end_time=log.timestamp,
                tenant_id=log.tenant_id
            )
            new_incident.threat_logs.append(log)
            db.add(new_incident)
            print(f"Created new incident for log {log.id}")

    db.commit()

def severity_to_numeric(severity: str) -> int:
    """Helper function to compare severity levels."""
    levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return levels.get(severity.lower(), 0)