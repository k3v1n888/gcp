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

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database
from ..auth.rbac import get_current_user
from ..predictive_service import get_next_threat_predictions
from ..models import User

router = APIRouter()

@router.get("/api/predictive/next_threat")
def get_next_threats(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    predictions = get_next_threat_predictions(db, current_user.tenant_id)
    return predictions
