from fastapi import APIRouter, Depends
from datetime import datetime
import torch
import random
from sqlalchemy.orm import Session

# Fix the imports - SessionLocal should come from database.py
from backend.database import SessionLocal, get_db
from backend.models import ThreatLog

router = APIRouter()

AGENT_NAMES = ["SIEM", "XDR", "ASM", "Network"]
THREATS = ["Ransomware", "Phishing", "DDoS", "C2 Communication"]

class SimpleThreatModel(torch.nn.Module):
    def __init__(self):
        super(SimpleThreatModel, self).__init__()
        self.linear = torch.nn.Linear(10, 1)

    def forward(self, x):
        return torch.sigmoid(self.linear(x))

models = {agent: SimpleThreatModel().to("cuda" if torch.cuda.is_available() else "cpu") for agent in AGENT_NAMES}

@router.get("/api/agents/threats")
def get_threat_predictions(db: Session = Depends(get_db)):  # Use proper type annotation
    response = []
    device = "cuda" if torch.cuda.is_available() else "cpu"
    for agent in AGENT_NAMES:
        model = models[agent]
        x = torch.randn(1, 10).to(device)
        score = model(x).item()
        if score > 0.5:
            threat_type = random.choice(THREATS)
            msg = f"AI predicts {threat_type} (confidence={score:.2f})"
            response.append({
                "agent": agent,
                "message": msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            # Fix ThreatLog creation with required fields
            log = ThreatLog(
                tenant_id=1,  # Add default tenant
                ip="127.0.0.1", 
                threat_type=threat_type,
                threat=threat_type, 
                source=agent,
                severity="medium",
                timestamp=datetime.utcnow()
            )
            db.add(log)
    db.commit()
    return response