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

import httpx
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

async def send_slack_alert(threat):
    if not SLACK_WEBHOOK_URL:
        return

    message = {
        "text": f":rotating_light: *{threat.get('severity', 'Unknown')} Threat Detected!*\n"
                f"*IP:* {threat['ip']}\n"
                f"*Threat:* {threat['threat']}\n"
                f"*Severity:* {threat.get('severity', 'N/A')}\n"
                f"*Source:* {threat['source']}\n"
                f"*Time:* {threat['timestamp']}"
    }

    async with httpx.AsyncClient() as client:
        await client.post(SLACK_WEBHOOK_URL, json=message)