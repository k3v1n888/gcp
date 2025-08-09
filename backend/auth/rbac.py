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
    ADDED: Development mode authentication bypass.
    """
    print("🔥 DEBUG: get_current_user called")
    
    # Development mode authentication bypass
    DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
    DISABLE_AUTH = os.getenv("DISABLE_GOOGLE_AUTH", "false").lower() == "true"
    AUTO_LOGIN = os.getenv("AUTO_LOGIN", "false").lower() == "true"
    
    if DEV_MODE or DISABLE_AUTH or AUTO_LOGIN:
        print("🔧 DEBUG: Development mode - bypassing authentication")
        db = SessionLocal()
        try:
            # Get or create a development user
            dev_user = db.query(User).filter(User.email == "dev@localhost.com").first()
            if not dev_user:
                print("🔧 DEBUG: Creating development user")
                # Create development user
                from backend.models import Tenant
                tenant = db.query(Tenant).first()
                if not tenant:
                    tenant = Tenant(name="Development Tenant", company="DevCorp")
                    db.add(tenant)
                    db.commit()
                    db.refresh(tenant)
                
                dev_user = User(
                    email="dev@localhost.com",
                    username="Developer",
                    role="admin",
                    tenant_id=tenant.id,
                    status="active"
                )
                db.add(dev_user)
                db.commit()
                db.refresh(dev_user)
                print("🔧 DEBUG: Development user created")
            
            print("🔧 DEBUG: Returning development user")
            return dev_user
        except Exception as e:
            print(f"🔧 DEBUG: Error creating/getting dev user: {e}")
            # Create a minimal user object for development
            class DevUser:
                def __init__(self):
                    self.id = 1
                    self.email = "dev@localhost.com"
                    self.username = "Developer"
                    self.role = "admin"
                    self.tenant_id = 1
                    self.status = "active"
            return DevUser()
        finally:
            try:
                db.close()
            except:
                pass
    
    # Production authentication
    session_user = request.session.get("user")
    if not session_user or not session_user.get("email"):
        print("🔥 DEBUG: No session user or email")
        raise HTTPException(status_code=401, detail="Not authenticated")

    print(f"🔥 DEBUG: Getting user for email: {session_user.get('email')}")
    db = SessionLocal()
    try:
        # Fetch the user from the database using the email from the session
        db_user = db.query(User).filter(User.email == session_user.get("email")).first()
        if not db_user:
            print("🔥 DEBUG: User not found in database")
            raise HTTPException(status_code=401, detail="User not found in database")
        
        print("🔥 DEBUG: User found, returning user object")
        # Return the full SQLAlchemy User object, which includes role and tenant_id
        return db_user
    except Exception as e:
        print(f"🔥 DEBUG: Database error in get_current_user: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        try:
            db.close()
            print("🔥 DEBUG: Database connection closed")
        except Exception as e:
            print(f"🔥 DEBUG: Error closing database: {e}")

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
