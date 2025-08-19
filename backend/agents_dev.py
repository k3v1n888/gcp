"""
Lightweight AI Agents for Development Environment
Optimized for CPU-only inference and reduced memory usage
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import random
import logging
import os
from typing import Dict, List, Any, Optional

# Conditional imports for lightweight development
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available, using mock predictions")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from backend.models import SessionLocal, ThreatLog

router = APIRouter()

# Agent configurations
AGENT_NAMES = ["SIEM", "XDR", "ASM", "Network", "Endpoint", "Email"]
THREATS = [
    "Ransomware", "Phishing", "DDoS", "C2 Communication", 
    "Lateral Movement", "Data Exfiltration", "Privilege Escalation",
    "Suspicious Login", "Malware Detection", "Anomalous Traffic"
]

# Feature names for SHAP explanations
FEATURE_NAMES = [
    "packet_size", "connection_duration", "bytes_sent", "bytes_received",
    "failed_logins", "unique_ports", "dns_requests", "http_requests",
    "ssh_attempts", "unusual_hours"
]

class LightweightThreatModel:
    """Lightweight threat detection model for development"""
    
    def __init__(self):
        if TORCH_AVAILABLE:
            self.model = nn.Sequential(
                nn.Linear(10, 32),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1),
                nn.Sigmoid()
            )
            # Load pre-trained weights if available
            model_path = "models/threat_detection_model.pth"
            if os.path.exists(model_path):
                try:
                    self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
                    logging.info(f"Loaded model from {model_path}")
                except Exception as e:
                    logging.warning(f"Could not load model: {e}")
            
            self.model.eval()
        else:
            self.model = None
    
    def predict(self, features: Optional[List[float]] = None) -> float:
        """Generate threat prediction score"""
        if self.model is not None and TORCH_AVAILABLE:
            if features is None:
                # Generate random features for demo
                features = torch.randn(1, 10)
            else:
                features = torch.tensor([features], dtype=torch.float32)
            
            with torch.no_grad():
                score = self.model(features).item()
            return score
        else:
            # Mock prediction for environments without PyTorch
            return random.uniform(0.1, 0.9)
    
    def get_shap_values(self, features: Optional[List[float]] = None) -> Dict[str, float]:
        """Generate SHAP-like feature importance values"""
        if features is None:
            # Generate mock feature importance
            importance = {
                name: random.uniform(-0.5, 0.5) 
                for name in FEATURE_NAMES
            }
        else:
            # Simple feature importance based on values
            importance = {
                FEATURE_NAMES[i]: features[i] * random.uniform(-0.1, 0.1)
                for i in range(min(len(features), len(FEATURE_NAMES)))
            }
        
        return importance

# Initialize models for each agent
models = {
    agent: LightweightThreatModel() 
    for agent in AGENT_NAMES
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_realistic_threat_data() -> Dict[str, Any]:
    """Generate realistic threat data for development/demo"""
    threat_type = random.choice(THREATS)
    base_score = random.uniform(0.3, 0.9)
    
    # Generate features that make sense for the threat type
    if threat_type == "Ransomware":
        features = [
            random.uniform(1000, 10000),  # packet_size
            random.uniform(300, 3600),    # connection_duration
            random.uniform(1000000, 10000000),  # bytes_sent
            random.uniform(100000, 1000000),    # bytes_received
            random.randint(0, 3),         # failed_logins
            random.randint(10, 50),       # unique_ports
            random.randint(5, 20),        # dns_requests
            random.randint(50, 200),      # http_requests
            random.randint(0, 5),         # ssh_attempts
            random.uniform(0, 1)          # unusual_hours (0-1)
        ]
    elif threat_type == "Phishing":
        features = [
            random.uniform(500, 2000),    # packet_size
            random.uniform(30, 300),      # connection_duration
            random.uniform(10000, 100000), # bytes_sent
            random.uniform(50000, 500000), # bytes_received
            random.randint(3, 10),        # failed_logins
            random.randint(1, 5),         # unique_ports
            random.randint(10, 50),       # dns_requests
            random.randint(100, 500),     # http_requests
            random.randint(0, 2),         # ssh_attempts
            random.uniform(0.2, 0.8)      # unusual_hours
        ]
    else:
        # Generic threat features
        features = [random.uniform(0, 10000) for _ in range(10)]
    
    return {
        "threat_type": threat_type,
        "features": features,
        "base_score": base_score
    }

@router.get("/api/agents/threats")
def get_threat_predictions(db: SessionLocal = Depends(get_db)):
    """Get AI threat predictions from all agents"""
    response = []
    
    try:
        for agent in AGENT_NAMES:
            model = models[agent]
            
            # Generate realistic threat scenario
            threat_data = generate_realistic_threat_data()
            
            # Get prediction
            score = model.predict(threat_data["features"])
            
            # Only include high-confidence threats
            if score > 0.5:
                threat_type = threat_data["threat_type"]
                
                # Generate SHAP values for explanation
                shap_values = model.get_shap_values(threat_data["features"])
                
                response_item = {
                    "agent": agent,
                    "threat_type": threat_type,
                    "confidence": round(score, 3),
                    "message": f"AI predicts {threat_type} (confidence={score:.2f})",
                    "timestamp": datetime.utcnow().isoformat(),
                    "shap_values": shap_values,
                    "features": {
                        FEATURE_NAMES[i]: threat_data["features"][i] 
                        for i in range(len(FEATURE_NAMES))
                    },
                    "risk_level": "HIGH" if score > 0.8 else "MEDIUM" if score > 0.6 else "LOW",
                    "recommendations": generate_recommendations(threat_type, score)
                }
                
                response.append(response_item)
                
                # Log to database
                try:
                    log = ThreatLog(
                        ip="127.0.0.1", 
                        threat=threat_type, 
                        source=agent,
                        confidence=score
                    )
                    db.add(log)
                except Exception as e:
                    logging.error(f"Failed to log threat: {e}")
        
        db.commit()
        
    except Exception as e:
        logging.error(f"Error generating threat predictions: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")
    
    return response

def generate_recommendations(threat_type: str, confidence: float) -> List[str]:
    """Generate security recommendations based on threat type"""
    base_recommendations = {
        "Ransomware": [
            "Immediately isolate affected systems",
            "Check backup integrity and availability",
            "Monitor for file encryption activities",
            "Update endpoint protection signatures"
        ],
        "Phishing": [
            "Block suspicious email senders",
            "Verify user credentials weren't compromised",
            "Conduct user awareness training",
            "Review email security policies"
        ],
        "DDoS": [
            "Enable DDoS protection services",
            "Monitor network bandwidth usage",
            "Implement rate limiting",
            "Contact ISP for upstream filtering"
        ],
        "C2 Communication": [
            "Block identified C2 domains/IPs",
            "Monitor for beaconing behavior",
            "Check for compromised endpoints",
            "Review network segmentation"
        ]
    }
    
    recommendations = base_recommendations.get(threat_type, [
        "Monitor system activities closely",
        "Review security logs",
        "Update security signatures",
        "Conduct thorough investigation"
    ])
    
    if confidence > 0.8:
        recommendations.insert(0, "URGENT: Take immediate action required")
    
    return recommendations

@router.get("/api/agents/status")
def get_agents_status():
    """Get status of all AI agents"""
    return {
        "agents": [
            {
                "name": agent,
                "status": "active",
                "model_loaded": models[agent].model is not None if TORCH_AVAILABLE else False,
                "last_prediction": datetime.utcnow().isoformat()
            }
            for agent in AGENT_NAMES
        ],
        "system_info": {
            "torch_available": TORCH_AVAILABLE,
            "numpy_available": NUMPY_AVAILABLE,
            "device": "cpu",
            "memory_usage": "optimized_for_development"
        }
    }

@router.post("/api/agents/retrain")
def retrain_models():
    """Mock endpoint for model retraining (development only)"""
    return {
        "status": "success",
        "message": "Models retrained successfully (mock)",
        "timestamp": datetime.utcnow().isoformat()
    }
