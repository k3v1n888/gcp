# backend/auth/rbac.py

from fastapi import Request, HTTPException, Depends
from backend.models import SessionLocal, User # You might not even need User/SessionLocal if roles are just from session user
from jose import jwt, JWTError
import os

# If you want to use the database for roles, keep SessionLocal and User.
# Otherwise, if roles are just stored in the session, you can remove these imports.

# Keep these if you intend to use JWT for other parts or in the future
# SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
# ALGORITHM = "HS256"

def get_current_user(request: Request):
    # <--- MODIFIED LOGIC: Use session data instead of JWT cookie
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Optional: If you need to fetch the user from the database to get their *current* role
    # or other database-persisted attributes, you'd do it here.
    # For a simple session-based authentication, the session 'user' dict might be enough.
    # If your 'user' dict in session includes the role, you can simplify even further.
    # Example if you need DB for roles (assuming 'email' is unique and linked to User):
    # db = SessionLocal()
    # db_user = db.query(User).filter(User.email == user.get("email")).first()
    # db.close()
    # if not db_user:
    #     raise HTTPException(status_code=401, detail="User not found in DB")
    # user["role"] = db_user.role # Update session user with DB role

    return user # Return the user dictionary from the session

def require_role(required_roles: list[str]): # Add type hint for clarity
    def role_checker(user: dict = Depends(get_current_user)): # User is now a dict from session
        # Assuming 'role' is part of the user dict stored in the session
        if user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
        return user
    return role_checker

# If your ThreatLog or other models use tenant_id from the user object,
# and the user object returned by get_current_user (from session) has 'tenant_id'.
# If not, you might need to adjust or fetch tenant_id from DB.
def get_tenant_id(user: dict = Depends(get_current_user)):
    return user.get("tenant_id") # Assuming tenant_id is in the session user dict