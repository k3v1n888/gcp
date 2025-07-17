import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

# --- 1. Adjust imports for new structure ---
# Import all necessary components from your project files
from .. import models, database, schemas
from ..models import User, Tenant
from ..database import get_db
from ..ueba_service import check_user_activity_anomaly

router = APIRouter()
oauth = OAuth()

# --- Configuration ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# This URL must exactly match what is in your Google Cloud OAuth Client ID settings
FRONTEND_URL = "https://quantum-ai.asia" 

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get('/api/auth/login')
async def login(request: Request):
    # --- FIX: Ensure the redirect_uri always uses https ---
    redirect_uri = f"{FRONTEND_URL}/api/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/api/auth/callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise Exception("No user info found in token")

        email = user_info.get('email')
        db_user = db.query(User).filter(User.email == email).first()

        if not db_user:
            # Create a default tenant and a new user
            tenant = Tenant(name=f"{user_info.get('name')}'s Tenant")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            db_user = User(
                username=user_info.get('name'), # Changed from 'name' to 'username' to match model
                email=email,
                role='admin',
                tenant_id=tenant.id
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # --- FIX: Use Pydantic schema for serialization, not the old .as_dict() ---
        pydantic_user = schemas.User.from_orm(db_user)
        request.session['user'] = pydantic_user.dict()
        
        # --- UEBA INTEGRATION ---
        # This logic is now correctly placed
        new_activity = models.UserActivityLog(
            user_id=db_user.id, 
            action="user_login", 
            details=f"Login from IP: {request.client.host}"
        )
        db.add(new_activity)
        db.commit()

        is_insider_anomaly = check_user_activity_anomaly(db, db_user, "user_login")
        if is_insider_anomaly:
            anomaly_threat = models.ThreatLog(
                ip=request.client.host,
                threat=f"UEBA: Anomalous login for user {db_user.username} outside of normal hours.",
                source="UEBA Engine",
                severity="high",
                tenant_id=db_user.tenant_id
            )
            db.add(anomaly_threat)
            db.commit()
        
        return RedirectResponse(url="/auth/success")

    except Exception as e:
        print(f"Error during auth callback: {e}")
        return RedirectResponse(url="/login?error=auth_failed")

@router.get("/api/auth/me")
def get_current_user(request: Request):
    user = request.session.get('user')
    if user:
        return user
    return None

@router.post("/api/auth/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/")
