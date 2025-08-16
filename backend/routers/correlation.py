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

# backend/routers/correlation.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database
from ..auth.rbac import get_current_user
from ..correlation_service import generate_holistic_summary
from ..models import User # Assuming User model is in models

router = APIRouter()

@router.get("/api/correlation/summary")
def get_correlation_summary(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    summary = generate_holistic_summary(db, current_user.tenant_id)
    return {"summary": summary}
