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

from fastapi import APIRouter
import httpx
import os

router = APIRouter()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

@router.post("/api/slack/alert")
async def slack_alert(payload: dict):
    threat = payload.get("threat")
    agent = payload.get("agent")
    message = f"🚨 *ALERT* 🚨\n*Threat:* {threat}\n*Detected by:* {agent}"

    try:
        response = httpx.post(SLACK_WEBHOOK_URL, json={"text": message})
        return {"status": "sent", "response": response.text}
    except Exception as e:
        return {"status": "failed", "error": str(e)}