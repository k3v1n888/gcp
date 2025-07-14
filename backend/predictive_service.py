import pandas as pd
from sqlalchemy.orm import Session
from . import models

def get_next_threat_predictions(db: Session, tenant_id: int) -> dict:
    """
    Analyzes the sequence of past threats to predict the most likely next threats.
    """
    # Get the last 100 threats in chronological order
    logs = db.query(models.ThreatLog.threat)\
             .filter(models.ThreatLog.tenant_id == tenant_id)\
             .order_by(models.ThreatLog.timestamp.asc())\
             .limit(100).all()
    
    if len(logs) < 2:
        return {"error": "Not enough data to make a prediction."}

    # Create a sequence of threats
    threat_sequence = [log[0] for log in logs]

    # Build a transition matrix (counts occurrences of threat B following threat A)
    transitions = {}
    for i in range(len(threat_sequence) - 1):
        current_threat = threat_sequence[i]
        next_threat = threat_sequence[i+1]
        
        if current_threat not in transitions:
            transitions[current_threat] = {}
        
        transitions[current_threat][next_threat] = transitions[current_threat].get(next_threat, 0) + 1

    # Get the last observed threat
    last_threat = threat_sequence[-1]

    # Find the most likely next threats based on what followed the last threat
    if last_threat in transitions:
        # Sort the possible next threats by frequency
        predictions = sorted(transitions[last_threat].items(), key=lambda item: item[1], reverse=True)
        # Return the top 3 predictions
        return {"last_observed": last_threat, "predictions": dict(predictions[:3])}

    return {"last_observed": last_threat, "predictions": {"No historical pattern found": 1}}
