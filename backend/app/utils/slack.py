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