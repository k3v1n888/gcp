import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

# --- 1. Adjust imports for new structure ---
from .. import models, database, schemas
from ..models import User, Tenant
from ..database import get_db
from ..ueba_service import check_user_activity_anomaly

router = APIRouter()
oauth = OAuth()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Use a default for development, but the environment variable in production
BASE_URL = os.getenv("BASE_URL", "https://quantum-ai.asia")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/api/auth/login')
async def login(request: Request):
    # Use the application's request URL to build the redirect URI
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/api/auth/callback', name='auth_callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise Exception("No user info found in token")

        email = user_info.get('email')
        db_user = db.query(User).filter(User.email == email).first()

        if not db_user:
            # Create a default tenant for the new user
            tenant = Tenant(name=f"{user_info.get('name')}'s Tenant")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            # Create a new user record
            db_user = User(
                username=user_info.get('name'),
                email=email,
                role='admin',  # Default role for new users
                tenant_id=tenant.id
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # --- 2. THIS IS THE FIX ---
        # Convert the SQLAlchemy object to a Pydantic model, then to a dictionary
        pydantic_user = schemas.User.from_orm(db_user)
        request.session['user'] = pydantic_user.dict()
        
        # --- UEBA INTEGRATION ---
        # 1. Log the successful login action
        new_activity = models.UserActivityLog(
            user_id=db_user.id, 
            action="user_login", 
            details=f"Login from IP: {request.client.host}"
        )
        db.add(new_activity)
        db.commit()

        # 2. Check for an anomaly
        is_insider_anomaly = check_user_activity_anomaly(db, db_user, "user_login")

        # 3. If it's an anomaly, create a new high-priority threat log
        if is_insider_anomaly:
            anomaly_threat = models.ThreatLog(
                ip=request.client.host,
                threat=f"UEBA: Anomalous login for user {db_user.username} outside of normal hours.",
                source="UEBA Engine",
                severity="high", # Assign a high severity to insider threats
                tenant_id=db_user.tenant_id
            )
            db.add(anomaly_threat)
            db.commit()
        
        # Redirect to the frontend success page
        return RedirectResponse(url="/auth/success")

    except Exception as e:
        print(f"Error during auth callback: {e}")
        return RedirectResponse(url="/login?error=auth_failed")

@router.get("/api/auth/me")
def get_current_user_api(request: Request):
    user = request.session.get('user')
    if user:
        return user
    return None

@router.post("/api/auth/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/")
