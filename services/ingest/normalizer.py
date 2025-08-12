
import re, yaml
from datetime import datetime, timezone
from jsonpath_ng import parse as jparse
from typing import Dict, Any, Union
from schemas import CanonicalEvent

def load_mapping(map_name: str) -> Dict[str, Any]:
    with open(f"mappings/{map_name}.yaml", "r") as f:
        return yaml.safe_load(f)

def save_mapping(name: str, yaml_text: str) -> None:
    with open(f"mappings/{name}.yaml","w") as f:
        f.write(yaml_text)

def _extract_json(fields_map: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, jp in fields_map.items():
        try:
            matches = [m.value for m in jparse(jp).find(payload)]
            out[k] = matches[0] if matches else None
        except Exception:
            out[k] = None
    return out

def _extract_syslog(pattern: str, line: str) -> Dict[str, Any]:
    m = re.search(pattern, line)
    return m.groupdict() if m else {}

def _to_int(v):
    try:
        return int(v)
    except Exception:
        return None

def normalize(raw: Union[Dict[str, Any], str], mapping: Dict[str, Any]) -> CanonicalEvent:
    vendor = mapping.get("vendor")
    product = mapping.get("product")
    event_type = mapping.get("event_type", "generic")

    if isinstance(raw, dict) and "fields" in mapping:
        fields = _extract_json(mapping["fields"], raw)
    elif isinstance(raw, str) and "syslog" in mapping:
        fields = _extract_syslog(mapping["syslog"]["pattern"], raw)
    else:
        fields = {}

    ts = fields.get("timestamp")
    if not ts:
        ts = datetime.now(timezone.utc).isoformat()

    evt = CanonicalEvent(
        timestamp=str(ts),
        vendor=vendor,
        product=product,
        event_type=event_type,
        severity=str(fields.get("severity")) if fields.get("severity") is not None else None,
        src_ip=fields.get("src_ip"),
        dst_ip=fields.get("dst_ip"),
        src_port=_to_int(fields.get("src_port")),
        dst_port=_to_int(fields.get("dst_port")),
        http_method=fields.get("http_method"),
        url=fields.get("url"),
        user=fields.get("user"),
        host=fields.get("host"),
        bytes_in=_to_int(fields.get("bytes_in")),
        bytes_out=_to_int(fields.get("bytes_out")),
        process_name=fields.get("process_name"),
        file_hash=fields.get("file_hash"),
        rule_name=fields.get("rule_name"),
        rule_id=fields.get("rule_id"),
        raw=raw if isinstance(raw, dict) else {"raw": raw},
    )
    return evt
