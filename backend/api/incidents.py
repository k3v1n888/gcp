from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import database, models, schemas
from ..auth.rbac import get_current_user

router = APIRouter()

@router.get("/api/incidents", response_model=List[schemas.SecurityIncident])
def get_open_incidents(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    incidents = db.query(models.SecurityIncident)\
        .filter(models.SecurityIncident.tenant_id == user.tenant_id)\
        .order_by(models.SecurityIncident.end_time.desc())\
        .limit(50).all()
    return incidents