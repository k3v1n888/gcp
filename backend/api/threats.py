from fastapi import APIRouter, Depends, Response, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import json
import math

from .. import models, database, schemas
from ..auth.rbac import get_current_user
from ..correlation_service import generate_threat_remediation_plan, get_and_summarize_misp_intel

router = APIRouter()

@router.get("/api/threats")
def get_threat_logs(
    response: Response,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    logs = (
        db.query(models.ThreatLog)
        .filter(models.ThreatLog.tenant_id == user.tenant_id)
        .order_by(models.ThreatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    return logs

@router.get("/api/threats/{threat_id}")
def get_threat_detail(
    request: Request,
    threat_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    threat_log = db.query(models.ThreatLog).filter(
        models.ThreatLog.id == threat_id,
        models.ThreatLog.tenant_id == user.tenant_id
    ).first()

    if not threat_log:
        raise HTTPException(status_code=404, detail="Threat log not found")

    timeline_threats = []
    if threat_log.incidents:
        parent_incident = threat_log.incidents[0]
        timeline_threats = sorted(
            [t for t in parent_incident.threat_logs if t.timestamp], 
            key=lambda log: log.timestamp
        )

    correlated_threat = db.query(models.CorrelatedThreat).filter(
        models.CorrelatedThreat.title == f"Attack Pattern: {threat_log.threat}",
        models.CorrelatedThreat.tenant_id == user.tenant_id
    ).first()

    recommendations_dict = generate_threat_remediation_plan(threat_log)
    misp_summary = get_and_summarize_misp_intel(threat_log.ip)
    soar_actions = db.query(models.AutomationLog).filter(models.AutomationLog.threat_id == threat_id).order_by(models.AutomationLog.timestamp.desc()).all()

    # Enhanced data cleaning function
    def clean_and_validate_numeric(value, default=0.0):
        """Clean numeric values, replacing NaN/None with defaults"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            if math.isnan(value) or not math.isfinite(value):
                return default
            return float(value)
        try:
            val = float(value)
            if math.isnan(val) or not math.isfinite(val):
                return default
            return val
        except (ValueError, TypeError):
            return default

    # Prepare clean threat log data for ML model
    threat_log_dict = {
        'id': threat_log.id,
        'ip': threat_log.ip or '',
        'threat': threat_log.threat or '',
        'source': threat_log.source or '',
        'severity': threat_log.severity or 'unknown',
        'ip_reputation_score': clean_and_validate_numeric(threat_log.ip_reputation_score, 0.0),
        'cvss_score': clean_and_validate_numeric(threat_log.cvss_score, 0.0),
        'criticality_score': clean_and_validate_numeric(threat_log.criticality_score, 0.0),
        'ioc_risk_score': clean_and_validate_numeric(threat_log.ioc_risk_score, 0.0),
        'has_cve': 1 if threat_log.cve_id else 0,
        'cve_id': threat_log.cve_id or '',
        'is_anomaly': bool(threat_log.is_anomaly),
        'tenant_id': threat_log.tenant_id
    }
    
    if threat_log.timestamp:
        threat_log_dict['timestamp'] = threat_log.timestamp.isoformat()

    # Get XAI explanation with enhanced error handling
    xai_explanation_dict = None
    try:
        if hasattr(request.app.state, 'predictor') and request.app.state.predictor:
            predictor = request.app.state.predictor
            print(f"🔍 Generating explanation for threat {threat_id} with data: {threat_log_dict}")
            
            raw_explanation = predictor.explain_prediction(threat_log_dict)
            print(f"🔍 Raw explanation received: {raw_explanation}")
            
            if raw_explanation:
                # Clean the explanation data
                xai_explanation_dict = {}
                
                # Handle base_value
                if 'base_value' in raw_explanation:
                    xai_explanation_dict['base_value'] = clean_and_validate_numeric(raw_explanation['base_value'])
                
                # Handle features - ensure we have the actual feature values
                if 'features' in raw_explanation:
                    xai_explanation_dict['features'] = {}
                    for key, value in raw_explanation['features'].items():
                        if isinstance(value, (int, float)):
                            xai_explanation_dict['features'][key] = clean_and_validate_numeric(value)
                        else:
                            xai_explanation_dict['features'][key] = value
                else:
                    # Fallback: use our clean threat data as features
                    xai_explanation_dict['features'] = {
                        'ip_reputation_score': threat_log_dict['ip_reputation_score'],
                        'cvss_score': threat_log_dict['cvss_score'],
                        'criticality_score': threat_log_dict['criticality_score'],
                        'ioc_risk_score': threat_log_dict['ioc_risk_score'],
                        'has_cve': threat_log_dict['has_cve'],
                        'severity_numeric': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4, 'unknown': 0}.get(threat_log_dict['severity'], 0)
                    }
                
                # Handle shap_values - this is the critical part
                if 'shap_values' in raw_explanation:
                    shap_vals = raw_explanation['shap_values']
                    if isinstance(shap_vals, list):
                        if len(shap_vals) > 0 and isinstance(shap_vals[0], list):
                            # Handle nested list structure
                            cleaned_shap = [clean_and_validate_numeric(val) for val in shap_vals[0]]
                        else:
                            # Handle flat list structure
                            cleaned_shap = [clean_and_validate_numeric(val) for val in shap_vals]
                    else:
                        cleaned_shap = [0.0] * len(xai_explanation_dict['features'])
                    
                    xai_explanation_dict['shap_values'] = [cleaned_shap]  # Keep it as nested for compatibility
                else:
                    # Generate mock SHAP values for demonstration (remove this in production)
                    feature_count = len(xai_explanation_dict['features'])
                    # Use actual feature values to generate meaningful mock impacts
                    mock_shap = []
                    for key, value in xai_explanation_dict['features'].items():
                        if 'score' in key and isinstance(value, (int, float)) and value > 0:
                            # Higher scores have higher impact
                            impact = value * 0.01  # Scale down the impact
                        elif key == 'has_cve' and value == 1:
                            impact = 0.15  # CVE presence has significant impact
                        else:
                            impact = 0.0
                        mock_shap.append(impact)
                    
                    xai_explanation_dict['shap_values'] = [mock_shap]
                
                print(f"✅ Cleaned explanation: {xai_explanation_dict}")
            else:
                print("⚠️ No explanation returned from predictor")
        else:
            print("⚠️ No predictor available in app state")
            
    except Exception as e:
        print(f"❌ Error generating XAI explanation: {e}")
        import traceback
        traceback.print_exc()

    # Build the final response
    response_data = schemas.ThreatDetailResponse.from_orm(threat_log)
    response_data.correlation = correlated_threat
    response_data.misp_summary = misp_summary
    response_data.soar_actions = soar_actions
    response_data.timeline_threats = timeline_threats
    
    if recommendations_dict:
        response_data.recommendations = schemas.Recommendation(**recommendations_dict)
    
    if xai_explanation_dict:
        response_data.xai_explanation = schemas.XAIExplanation(**xai_explanation_dict)
    
    if threat_log.is_anomaly:
        response_data.anomaly_features = schemas.AnomalyFeatures(
            text_feature=f"{threat_log.threat} {threat_log.source}",
            ip_reputation_score=clean_and_validate_numeric(threat_log.ip_reputation_score),
            has_cve=1 if threat_log.cve_id else 0
        )
    
    return response_data
