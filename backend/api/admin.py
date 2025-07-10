from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Adjust imports to match your project structure
from .. import database, models, schemas

# This Pydantic model validates the incoming data when saving settings
class SettingsUpdate(BaseModel):
    alert_severity: str

router = APIRouter()

@router.get("/api/admin/settings", response_model=schemas.SystemSettings)
def get_settings(db: Session = Depends(database.get_db), local_kw: str = ""):
    """
    This correctly defines `db` as a dependency and `local_kw` as an
    optional query parameter.
    """
    settings = db.query(models.SystemSettings).first()

    # If no settings exist in the database yet, create a default one
    if not settings:
        default_settings = models.SystemSettings(alert_severity="critical")
        db.add(default_settings)
        db.commit()
        db.refresh(default_settings)
        return default_settings
        
    return settings


@router.post("/api/admin/settings")
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(database.get_db)):
    """
    Finds the existing settings record (or creates one) and updates it.
    """
    settings = db.query(models.SystemSettings).first()

    if not settings:
        settings = models.SystemSettings()
        db.add(settings)

    settings.alert_severity = settings_update.alert_severity
    db.commit()
    
    return {"message": "Settings updated successfully"}
