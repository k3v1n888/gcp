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

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .. import database, models
from ..auth.rbac import get_current_user
from ..threat_hunting_service import run_ai_threat_hunt

router = APIRouter()

@router.post("/api/hunting/run")
def run_new_hunt(
    request: Request, 
    user: models.User = Depends(get_current_user), 
    db: Session = Depends(database.get_db)
):
    # The predictor is no longer needed here, as the hunting service calls the AI service directly
    hunt_results = run_ai_threat_hunt(db, user.tenant_id)
    return hunt_results