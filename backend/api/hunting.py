from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .. import database, models
from ..auth.rbac import get_current_user
from ..threat_hunting_service import run_ai_threat_hunt

router = APIRouter()

@router.post("/api/hunting/run")
def run_new_hunt(request: Request, user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    predictor = request.app.state.predictor
    hunt_results = run_ai_threat_hunt(db, predictor, user.tenant_id)
    return hunt_results