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
