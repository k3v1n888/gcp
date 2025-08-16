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
from pydantic import BaseModel
from typing import List, Dict, Any
from ..correlation_service import generate_threat_remediation_plan

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    threat_context: Dict[str, Any]
    history: List[ChatMessage]

@router.post("/api/chat")
async def handle_chat(request: ChatRequest):
    class TmpLog:
        def __init__(self, d): self.__dict__ = d
    
    threat_log_obj = TmpLog(request.threat_context)
    ai_response = generate_threat_remediation_plan(threat_log_obj)

    if ai_response and 'mitigation' in ai_response:
        response_content = "Based on the threat details, here are the mitigation steps: \n - " + "\n - ".join(ai_response.get('mitigation', []))
    else:
        response_content = "I was unable to generate specific mitigation steps for this query."

    return {"role": "assistant", "content": response_content}
