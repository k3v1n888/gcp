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

import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter
import os

router = APIRouter()

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

@router.post("/api/alert")
def send_alert(payload: dict):
    threat = payload.get("threat")
    agent = payload.get("agent")
    message = f"Critical threat detected by {agent}: {threat}"
    msg = MIMEText(message)
    msg["Subject"] = "[ALERT] Cyber Threat Detected"
    msg["From"] = EMAIL_USER
    msg["To"] = ALERT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, ALERT_EMAIL, msg.as_string())
        return {"status": "sent"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}