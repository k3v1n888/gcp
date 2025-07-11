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
