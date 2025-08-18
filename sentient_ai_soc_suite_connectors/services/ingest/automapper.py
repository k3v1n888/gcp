"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire


from typing import Dict, Any
import yaml

def json_keys_flat(d: Dict[str, Any], prefix=""):
    keys = []
    for k,v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        keys.append(path)
        if isinstance(v, dict):
            keys.extend(json_keys_flat(v, path))
    return keys

def propose_json_mapping(sample: Dict[str, Any]) -> Dict[str,str]:
    mapping = {}
    candidates = {
        "timestamp": ["eventTime","timestamp","time","@timestamp","when"],
        "severity": ["severity","rule.level","level"],
        "src_ip": ["sourceIPAddress","src_ip","client.ip","client_ip","agent.ip"],
        "user": ["userIdentity.userName","user","actor.name","principalId"],
        "url": ["requestParameters.requestURL","url","request_uri"],
        "http_method": ["requestParameters.httpMethod","method","http_method"],
        "bytes_in": ["data.bytes_in","bytes_in","bytesIn","bytesInCount"],
        "bytes_out": ["data.bytes_out","bytes_out","bytesOutCount","bytesOut"],
        "rule_name": ["rule.description","ruleName","signature"],
        "rule_id": ["rule.id","ruleId","signature_id"]
    }
    flat = set(json_keys_flat(sample))
    for tgt, options in candidates.items():
        for opt in options:
            if opt in flat:
                mapping[tgt] = f"$.{opt}"
                break
    return mapping

def build_yaml(source_name: str, mapping: Dict[str,str], vendor="Unknown", product="Unknown", event_type="generic"):
    doc = {
        "vendor": vendor,
        "product": product,
        "event_type": event_type,
        "fields": mapping
    }
    return yaml.safe_dump(doc, sort_keys=False)
