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
