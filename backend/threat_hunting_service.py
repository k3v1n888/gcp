import pandas as pd
from sqlalchemy.orm import Session
from . import models
from .wazuh_service import get_wazuh_jwt, WAZUH_URL
import requests

def run_ai_threat_hunt(db: Session, predictor_model, tenant_id: int):
    """
    Uses the AI model's knowledge to generate and run proactive threat hunting queries.
    """
    print("Starting AI-Driven Threat Hunt...")
    if not predictor_model:
        return {"error": "Severity prediction model not loaded."}

    try:
        # --- 1. Extract Top Indicators from the AI Model ---
        # Get the actual logistic regression classifier from the pipeline
        classifier = predictor_model.named_steps['logisticregression']
        # Get the TfidfVectorizer to understand the feature names
        vectorizer = predictor_model.named_steps['columntransformer'].named_transformers_['text']
        
        # Find the "critical" class index
        critical_class_index = list(classifier.classes_).index('critical')
        # Get the weights (coefficients) for the critical class
        critical_coefs = classifier.coef_[critical_class_index]
        
        # Get the feature names from the vectorizer
        feature_names = vectorizer.get_feature_names_out()
        
        # Create a DataFrame of features and their weights
        coef_df = pd.DataFrame({'feature': feature_names, 'coef': critical_coefs})
        # Get the top 5 features with the highest positive weights
        top_indicators = coef_df.sort_values(by='coef', ascending=False).head(5)
        
        print(f"Top indicators for 'critical' threats: {top_indicators['feature'].tolist()}")

        # --- 2. Generate and Run Hunting Queries ---
        jwt_token = get_wazuh_jwt()
        if not jwt_token:
            return {"error": "Could not authenticate with Wazuh for threat hunt."}

        all_results = []
        for indicator in top_indicators['feature']:
            # Create a simple query to search for this indicator in Wazuh logs
            wazuh_query = f'"{indicator}"' # Search for the exact keyword
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
        
        # Save hunt results to the database (simplified for this example)
        new_hunt = models.ThreatHunt(
            status="completed",
            query=str(top_indicators['feature'].tolist()),
            results={"found_alerts": all_results},
            tenant_id=tenant_id
        )
        db.add(new_hunt)
        db.commit()
        
        print(f"✅ Threat Hunt complete. Found {len(all_results)} potential stealthy threats.")
        return new_hunt

    except Exception as e:
        print(f"❌ Threat Hunt failed: {e}")
        return {"error": str(e)}