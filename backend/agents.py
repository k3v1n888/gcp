from fastapi import APIRouter, Depends
from datetime import datetime
import torch
import random
from sqlalchemy.orm import Session

# Restore original import
from backend.models import SessionLocal, ThreatLog

router = APIRouter()

# Keep all your original code exactly as it was
AGENT_NAMES = ["SIEM", "XDR", "ASM", "Network"]
THREATS = ["Ransomware", "Phishing", "DDoS", "C2 Communication"]

class SimpleThreatModel(torch.nn.Module):
    def __init__(self):
        super(SimpleThreatModel, self).__init__()
        self.linear = torch.nn.Linear(10, 1)

    def forward(self, x):
        return torch.sigmoid(self.linear(x))

models = {agent: SimpleThreatModel().to("cuda" if torch.cuda.is_available() else "cpu") for agent in AGENT_NAMES}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/agents/threats")
def get_threat_predictions(db: Session = Depends(get_db)):
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
            log = ThreatLog(
                tenant_id=1,
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