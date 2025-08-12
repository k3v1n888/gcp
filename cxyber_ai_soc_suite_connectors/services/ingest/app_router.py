
from fastapi import APIRouter, Body
from typing import Dict, Any
from router import route
from automapper import propose_json_mapping, build_yaml
from normalizer import load_mapping, normalize, save_mapping
from enrichers import enrich_and_featureize
from schemas import FeatureVector, CanonicalEvent

r = APIRouter()

@r.get("/mappings")
def list_mappings():
    import os
    files = [f for f in os.listdir("mappings") if f.endswith(".yaml")]
    return {"mappings": files}

@r.post("/approve_mapping")
def approve_mapping(payload: Dict[str, str] = Body(...)):
    name = payload.get("name")
    yaml_text = payload.get("yaml_text")
    if not name or not yaml_text:
        return {"ok": False, "error": "name and yaml_text required"}
    save_mapping(name, yaml_text)
    return {"ok": True, "saved_as": f"mappings/{name}.yaml"}

@r.post("/ingest_auto")
def ingest_auto(payload: Dict[str, Any] = Body(...)):
    source, conf = route(payload)
    if source != "unknown" and conf >= 0.8:
        mapping = load_mapping(source)
        ce = normalize(payload, mapping)
        fv = enrich_and_featureize(ce)
        return {"mode":"parsed", "source":source, "confidence":conf,
                "feature_vector": fv.model_dump(), "canonical_event": ce.model_dump()}
    proposal = propose_json_mapping(payload)
    yaml_text = build_yaml("auto_new_source", proposal)
    return {"mode":"proposed", "source":"unknown", "confidence":conf, "proposed_mapping_yaml": yaml_text}
