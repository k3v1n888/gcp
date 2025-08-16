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

from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/api/graph/storyline/{threat_id}")
def get_storyline(request: Request, threat_id: int):
    graph_service = request.app.state.graph_service
    storyline = graph_service.get_attack_storyline(threat_id)
    return {"storyline": storyline}