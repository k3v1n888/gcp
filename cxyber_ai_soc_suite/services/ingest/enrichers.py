
from typing import Optional, List
from schemas import CanonicalEvent, FeatureVector

def compute_criticality(ip_rep: Optional[int], cvss: Optional[float]) -> Optional[float]:
    if ip_rep is None or cvss is None:
        return None
    return round(0.5 * (ip_rep / 100.0) + 0.5 * (cvss / 10.0), 4)

def map_to_mitre(evt: CanonicalEvent) -> List[str]:
    ttp = []
    try:
        if evt.event_type == "waf" and evt.url and "union select" in evt.url.lower():
            ttp.append("TA0001")  # example only
        if evt.event_type == "edr" and evt.process_name and evt.process_name.lower().startswith("powershell"):
            ttp.append("TA0002")
    except Exception:
        pass
    return ttp

def enrich_and_featureize(evt: CanonicalEvent,
                          ip_rep_score: Optional[int] = None,
                          cvss_score: Optional[float] = None,
                          asset_criticality: Optional[float] = None,
                          anomaly_hint: Optional[int] = None) -> FeatureVector:
    mitre = map_to_mitre(evt)
    crit = compute_criticality(ip_rep_score, cvss_score)
    return FeatureVector(
        ip_reputation=ip_rep_score,
        cvss_score=cvss_score,
        criticality_score=crit,
        mitre_tactics=mitre,
        asset_criticality=asset_criticality,
        bytes_received=evt.bytes_in,
        bytes_sent=evt.bytes_out,
        is_anomaly_hint=anomaly_hint,
        source=f"{evt.vendor or ''}:{evt.product or ''}",
        extra={"rule_name": evt.rule_name, "user": evt.user, "host": evt.host}
    )
