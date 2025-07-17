# backend/ueba_service.py
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timedelta

def check_user_activity_anomaly(db: Session, user: models.User, action: str) -> bool:
    """A simple UEBA check for anomalous login times."""
    if action != "user_login":
        return False

    recent_logins = db.query(models.UserActivityLog.timestamp)\
        .filter(
            models.UserActivityLog.user_id == user.id,
            models.UserActivityLog.action == "user_login",
            models.UserActivityLog.timestamp > datetime.utcnow() - timedelta(days=30)
        ).all()

    if len(recent_logins) < 5: # Need at least 5 logins to establish a baseline
        return False

    login_hours = [t[0].hour for t in recent_logins]
    baseline_hour = max(set(login_hours), key=login_hours.count)
    
    current_hour = datetime.utcnow().hour
    is_off_hours = abs(current_hour - baseline_hour) > 4

    if is_off_hours:
        print(f"UEBA Anomaly Detected for user {user.username}: Login at unusual hour {current_hour} UTC.")
        return True
        
    return False
