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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .. import database, models, schemas
from ..auth.rbac import get_current_user # Assuming you have this for getting the logged-in user

class SettingsUpdate(BaseModel):
    alert_severity: str

router = APIRouter()

@router.get("/api/admin/settings", response_model=schemas.SystemSettings)
def get_settings(db: Session = Depends(database.get_db), local_kw: str = ""):
    settings = db.query(models.SystemSettings).first()
    if not settings:
        default_settings = models.SystemSettings(alert_severity="critical")
        db.add(default_settings)
        db.commit()
        db.refresh(default_settings)
        return default_settings
    return settings

@router.post("/api/admin/settings")
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(database.get_db)):
    settings = db.query(models.SystemSettings).first()
    if not settings:
        settings = models.SystemSettings()
        db.add(settings)
    settings.alert_severity = settings_update.alert_severity
    db.commit()
    return {"message": "Settings updated successfully"}

# --- NEW: Endpoint to invite a new user ---
@router.post("/api/admin/invite", status_code=201)
def invite_user(
    invite_data: schemas.UserInviteRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can invite new users.")

    existing_user = db.query(models.User).filter(models.User.email == invite_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    new_user = models.User(
        email=invite_data.email,
        role=invite_data.role,
        status="pending",
        tenant_id=current_user.tenant_id,
        username=invite_data.email # Use email as a temporary username
    )
    db.add(new_user)
    db.commit()

    return {"message": f"User {invite_data.email} successfully invited with role '{invite_data.role}'."}
