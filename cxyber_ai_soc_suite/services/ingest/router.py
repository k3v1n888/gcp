
from typing import Dict, Any, Tuple, Set

KNOWN = {
    "wazuh": {"rule.level","rule.description","agent.ip","agent.name","data.bytes_in"},
    "cloudtrail": {"eventTime","userIdentity.userName","sourceIPAddress","eventName","requestParameters.httpMethod"},
    "syslog_f5_waf": {"_syslog"}  # non-JSON marker
}

def _json_keys_flat(d: Dict[str, Any], prefix: str = "") -> Set[str]:
    keys = set()
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        keys.add(path)
        if isinstance(v, dict):
            keys |= _json_keys_flat(v, path)
    return keys

def _jaccard(a: Set[str], b: Set[str]) -> float:
    inter = len(a & b); union = len(a | b)
    return inter/union if union else 0.0

def route(payload: Any) -> Tuple[str, float]:
    if isinstance(payload, str):
        return "syslog_f5_waf", 0.9
    if not isinstance(payload, dict):
        return "unknown", 0.0
    keys = _json_keys_flat(payload)
    if "eventTime" in keys: return "cloudtrail", 0.85
    if "rule.level" in keys: return "wazuh", 0.85
    best, score = "unknown", 0.0
    for name, sig in KNOWN.items():
        s = _jaccard(keys, sig)
        if s > score:
            best, score = name, s
    return best, score
