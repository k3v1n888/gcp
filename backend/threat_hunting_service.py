import pandas as pd
from sqlalchemy.orm import Session
from . import models
from .wazuh_service import get_wazuh_jwt, WAZUH_URL
import requests
from datetime import datetime, timezone

def run_ai_threat_hunt(db: Session, predictor, tenant_id: int):
    """
    Uses the AI model's knowledge to generate and run proactive threat hunting queries.
    """
    print("Starting AI-Driven Threat Hunt...")
    if not predictor or not predictor.model:
        return {"error": "Severity prediction model not loaded."}

    try:
        # --- THIS IS THE FIX: Access the model pipeline directly from the predictor object ---
        pipeline = predictor.model
        classifier = pipeline.named_steps['logisticregression']
        vectorizer = pipeline.named_steps['columntransformer'].named_transformers_['text']
        
        critical_class_index = list(classifier.classes_).index('critical')
        critical_coefs = classifier.coef_[critical_class_index]
        
        feature_names = vectorizer.get_feature_names_out()
        
        coef_df = pd.DataFrame({'feature': feature_names, 'coef': critical_coefs})
        top_indicators = coef_df.sort_values(by='coef', ascending=False).head(5)
        
        print(f"Top indicators for 'critical' threats: {top_indicators['feature'].tolist()}")

        jwt_token = get_wazuh_jwt()
        if not jwt_token:
            return {"error": "Could not authenticate with Wazuh for threat hunt."}

        all_results = []
        for indicator in top_indicators['feature']:
            wazuh_query = f'"{indicator}"'
            print(f"Hunting in Wazuh for: {wazuh_query}")
            
            response = requests.get(
                f"{WAZUH_URL}/alerts",
                params={'q': wazuh_query, 'limit': 10},
                headers={'Authorization': f'Bearer {jwt_token}'},
                verify=False
            )
            if response.ok:
                results = response.json().get('data', {}).get('affected_items', [])
                all_results.extend(results)
        
        new_hunt = models.ThreatHunt(
            status="completed",
            query=str(top_indicators['feature'].tolist()),
            results={"found_alerts": all_results},
            tenant_id=tenant_id,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(new_hunt)
        db.commit()
        
        print(f"✅ Threat Hunt complete. Found {len(all_results)} potential stealthy threats.")
        return new_hunt

    except Exception as e:
        print(f"❌ Threat Hunt failed: {e}")
        return {"error": str(e)}