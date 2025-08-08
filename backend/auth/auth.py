import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from .. import models, database, schemas
from ..models import User, Tenant
from ..database import get_db
from ..ueba_service import check_user_activity_anomaly

router = APIRouter()
oauth = OAuth()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://qai.quantum-ai.asia")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get('/api/auth/login')
async def login(request: Request):
    redirect_uri = f"{FRONTEND_URL}/api/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/api/auth/callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise Exception("No user info found")

        email = user_info.get('email')
        db_user = db.query(User).filter(User.email == email).first()

        if db_user:
            # --- HANDLE INVITED USERS ---
            if db_user.status == 'pending':
                db_user.username = user_info.get('name')
                db_user.status = 'active'
                db.commit()
                db.refresh(db_user)
        else:
            # --- HANDLE BRAND NEW USERS (Not previously invited) ---
            tenant = Tenant(name=f"{user_info.get('name')}'s Tenant")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            db_user = User(
                username=user_info.get('name'),
                email=email,
                role='admin',
                tenant_id=tenant.id,
                status='active'
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # Use the existing as_dict() method from your User model
        request.session['user'] = db_user.as_dict()
        request.session['id_token'] = token['id_token']
        
        # UEBA Integration
        new_activity = models.UserActivityLog(user_id=db_user.id, action="user_login", details=f"Login from IP: {request.client.host}")
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
        
        response = RedirectResponse(url="/auth/success")
        response.set_cookie(
            key="session",
            value=token['id_token'],
            httponly=True,
            samesite="none",
            secure=True,
        )
        return response
    except Exception as e:
        print(f"Error during auth callback: {e}")
        return RedirectResponse(url="/login?error=auth_failed")

@router.get("/api/auth/me")
def get_current_user_from_session(request: Request):
    print("🔥 DEBUG: /api/auth/me endpoint called")
    try:
        user = request.session.get('user')
        print(f"🔥 DEBUG: Session user: {user is not None}")
        if user:
            print("🔥 DEBUG: Returning user session data")
            return user
        print("🔥 DEBUG: No user in session, returning None")
        return None
    except Exception as e:
        print(f"🔥 DEBUG: Error in /api/auth/me: {e}")
        raise

@router.post("/api/auth/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    request.session.pop('id_token', None)
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    return response
