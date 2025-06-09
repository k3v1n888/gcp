# backend/auth/rbac.py

from fastapi import Request, HTTPException, Depends
from backend.models import SessionLocal, User
from jose import jwt, JWTError
import os

def get_current_user(request: Request):
    """
    MODIFIED: Use session data to get the user's email, then fetch the full
    user object (including role and tenant) from the database.
    This ensures that role changes are reflected immediately.
    """
    session_user = request.session.get("user")
    if not session_user or not session_user.get("email"):
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        # Fetch the user from the database using the email from the session
        db_user = db.query(User).filter(User.email == session_user.get("email")).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="User not found in database")
        
        # Return the full SQLAlchemy User object, which includes role and tenant_id
        return db_user
    finally:
        db.close()

def require_role(required_roles: list[str]):
    def role_checker(user: User = Depends(get_current_user)): # User is now a User model instance
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
        return user
    return role_checker

def get_tenant_id(user: User = Depends(get_current_user)):
    """
    Gets the tenant_id from the authenticated user object.
    """
    return user.tenant_id
