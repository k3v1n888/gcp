# backend/routers/debug.py

from fastapi import APIRouter
from ..correlation_service import get_ip_reputation

router = APIRouter()

@router.get("/api/debug/ip_check")
def check_ip_reputation(ip: str):
    """
    A simple endpoint to test the get_ip_reputation function in isolation.
    """
    print(f"--- DEBUG: Checking reputation for IP: {ip} ---")
    score = get_ip_reputation(ip)
    print(f"--- DEBUG: Received score: {score} ---")
    
    return {"ip_checked": ip, "abuse_score": score}
