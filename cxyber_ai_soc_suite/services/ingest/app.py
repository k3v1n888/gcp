
from fastapi import FastAPI, Body, Query
from typing import Union, Dict, Any
from schemas import FeatureVector
from normalizer import load_mapping, normalize
from enrichers import enrich_and_featureize
from app_router import r

app = FastAPI(title="Ingest Service (AI Router)", version="0.2.0")
app.include_router(r)

@app.post("/ingest/{source}", response_model=FeatureVector)
def ingest_and_transform(
    source: str,
    payload: Union[Dict[str, Any], str] = Body(..., description="JSON dict or raw syslog line"),
    ip_rep_score: int | None = Query(default=None),
    cvss_score: float | None = Query(default=None),
    asset_criticality: float | None = Query(default=None),
    anomaly_hint: int | None = Query(default=None)
) -> FeatureVector:
    mapping = load_mapping(source)
    ce = normalize(payload, mapping)
    fv = enrich_and_featureize(ce, ip_rep_score, cvss_score, asset_criticality, anomaly_hint)
    return fv
