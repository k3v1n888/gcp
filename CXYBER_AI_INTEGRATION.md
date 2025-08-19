# 🤖 CXyber AI SOC Multi-Model Integration Guide

## System Architecture Overview

Your CXyber AI SOC system now implements the complete 3-model architecture designed with GPT-5:

```
[Security Tools] → Model A → Model B → Model C → [Actions]
     ↓              ↓         ↓         ↓         ↓
[Raw Events]   [Normalized] [Enriched] [Predicted] [Executed]
```

## 🧠 AI Models Integration

### Model A: Data Intake & Normalization AI
- **Service**: `ingest-service` (Port 8000)
- **Purpose**: Auto-detects source type, normalizes to CXyber schema
- **Your Implementation**: `services/ingest/app.py`
- **Key Endpoints**:
  - `POST /ingest_auto` - Auto-detect and normalize
  - `POST /approve_mapping` - Approve new source mappings
- **Output**: FeatureVector with standardized fields

### Model B: Post-Processing & Enrichment AI  
- **Service**: `postprocess-service` (Port 8001)
- **Purpose**: Enriches with threat intelligence, MISP, CVE data
- **Your Implementation**: `backend/` services with AI orchestration
- **Features**:
  - MISP integration for IoCs
  - CVE scoring and correlation
  - IP reputation analysis
  - Risk scoring algorithms
- **Output**: Enhanced data with criticality scores

### Model C: Quantum AI Predictive Security Engine
- **Service**: `threat-model` (Port 9000) + `threat-service` (Port 8002)
- **Purpose**: Your trained ML models for threat prediction + SHAP explanations
- **Your Implementation**: `ai-service/main.py` with your `.joblib` models
- **Key Features**:
  - RandomForest classifier with your training data
  - SHAP explainable AI
  - Anomaly detection (Isolation Forest)
  - Real-time threat scoring
- **Output**: Severity, confidence, findings, SHAP values

## 🔄 Data Flow Integration

### 1. Input Processing
```bash
curl -X POST http://localhost:8000/ingest_auto \
  -H "Content-Type: application/json" \
  -d '{"raw_event": "your_security_log", "source_hint": "waf"}'
```

### 2. Enrichment Pipeline
The enriched data flows automatically to your threat model:
```json
{
  "cvss_score": 8.5,
  "criticality_score": 0.9,
  "ioc_risk_score": 85,
  "technique_id": "T1190",
  "is_admin": 1
}
```

### 3. AI Prediction
Your trained models analyze and return:
```json
{
  "severity": "critical",
  "confidence": 0.92,
  "findings": ["SQL Injection", "High CVSS Score", "IoC Match"],
  "shap": {
    "cvss_score": 0.4,
    "criticality_score": 0.3,
    "ioc_risk_score": 0.2
  }
}
```

### 4. Orchestrated Actions
```bash
curl -X POST http://localhost:8003/actions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action_plan": [
      {"action": "notify", "channel": "#soc", "priority": "p1"},
      {"action": "ticket", "template": "critical-incident"}
    ]
  }'
```

## 🎛 Service Configuration

### Environment Variables
```bash
# Model Integration
export REMOTE_MODEL_URL=http://threat-model:8001/predict

# Orchestration Connectors
export SLACK_WEBHOOK_URL=your_slack_webhook
export TEAMS_WEBHOOK_URL=your_teams_webhook
export JIRA_BASE_URL=your_jira_url
export JIRA_EMAIL=your_email
export JIRA_API_TOKEN=your_token

# Database
export DATABASE_URL=postgresql://user:password@db:5432/cyberdb
export REDIS_URL=redis://redis:6379
```

## 🚀 Quick Start

### Start Complete System
```bash
./start-cxyber-soc.sh
```

### Individual Services (Development)
```bash
# Model A: Ingest Service
cd services/ingest && uvicorn app:app --reload --port 8000

# Model B: Backend Services  
cd backend && uvicorn main:app --reload --port 8001

# Model C: Your AI Models
cd ai-service && python main.py

# Threat Service Wrapper
cd services/threat_service && uvicorn app:app --reload --port 8002

# Orchestrator
cd services/orchestrator && uvicorn app:app --reload --port 8003
```

## 🧪 Testing Your Models

### Test Model A (Normalization)
```bash
curl -X POST http://localhost:8000/ingest_auto \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-08-13T10:00:00Z",
    "message": "SQL injection attempt detected",
    "source_ip": "192.168.1.100",
    "tool": "waf"
  }'
```

### Test Model C (Your Trained Model)
```bash
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "technique_id": "T1190",
      "cvss_score": 9.8,
      "criticality_score": 0.95,
      "ioc_risk_score": 90,
      "is_admin": 1,
      "login_hour": 2
    }
  }'
```

### Test Complete Pipeline
```bash
curl -X POST http://localhost:8002/threat/score \
  -H "Content-Type: application/json" \
  -d '{
    "feature_vector": {
      "criticality_score": 0.9,
      "ip_reputation": 15
    },
    "canonical_event": {
      "event_type": "waf",
      "url": "union select * from users"
    },
    "context": {}
  }'
```

## 🔧 Model Enhancement

### Add New Data Source
1. Send unknown format to Model A
2. Approve mapping via Console: http://localhost:8005
3. System auto-learns the new source format

### Improve Model C Predictions
```bash
curl -X POST http://localhost:9000/partial_fit \
  -H "Content-Type: application/json" \
  -d '{
    "features": {...},
    "true_label": "critical",
    "feedback": "false_negative"
  }'
```

### Monitor Model Drift
```bash
curl http://localhost:9000/drift_check
```

## 🔍 Monitoring & Observability

### Health Checks
- Model A: `GET http://localhost:8000/health`
- Model B: `GET http://localhost:8001/health` 
- Model C: `GET http://localhost:9000/health`
- Threat Service: `GET http://localhost:8002/health`
- Orchestrator: `GET http://localhost:8003/health`

### Service Logs
```bash
# All services
docker-compose -f docker-compose.cxyber.yml logs -f

# Specific service
docker-compose -f docker-compose.cxyber.yml logs -f threat-model
```

### Performance Metrics
- View real-time model performance in dashboard: http://localhost:3000
- API metrics available at each service's `/metrics` endpoint

## 🛡 Security & Compliance

### Data Privacy
- PII masking in Model A ingest layer
- Secure model artifact storage
- Encrypted inter-service communication

### Audit Trail
- All AI decisions logged with explanations
- Model version tracking
- Analyst feedback integration

## 🔮 Quantum Roadmap

### Phase 1: Classical-Quantum Hybrid (Current)
- ✅ Classical ML with quantum-inspired algorithms
- ✅ SHAP explainability for transparency
- ✅ Multi-model orchestration

### Phase 2: Quantum Enhancement (Next)
- [ ] Qiskit integration for correlation optimization
- [ ] Quantum anomaly detection algorithms
- [ ] Quantum-enhanced feature selection

### Phase 3: Full Quantum SOC (Future)
- [ ] Quantum ML for threat prediction
- [ ] Quantum cryptography for secure comms
- [ ] Quantum-accelerated incident response

## 📚 Integration References

- **FastAPI Docs**: Each service exposes OpenAPI docs at `/docs`
- **Model Schemas**: `shared/schemas.py` for consistent data contracts
- **Connector Templates**: `services/orchestrator/connectors.py`
- **Mapping Examples**: `services/ingest/mappings/` directory

---

🎯 **Your CXyber AI SOC system is now a complete multi-model architecture with your trained threat detection models at the core!**
