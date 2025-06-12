# backend/auth/auth.py

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from backend.models import User, Tenant
from backend.database import get_db

router = APIRouter()
oauth = OAuth()

# This should match your setup
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://quantum-ai.asia")

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
    redirect_uri = f"{FRONTEND_URL}/api/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/api/auth/callback')
async def auth_callback(request: Request, db=Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise Exception("No user info found")

        email = user_info.get('email')
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Create a default tenant for the new user
            tenant = Tenant(name=f"{user_info.get('name')}'s Tenant")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            user = User(
                name=user_info.get('name'),
                email=email,
                picture=user_info.get('picture'),
                role='admin',  # Default role for new users
                tenant_id=tenant.id
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        request.session['user'] = user.as_dict()
        request.session['id_token'] = token['id_token']
        
        # --- THIS IS THE CHANGE ---
        # Instead of going to /dashboard, we go to a special frontend route.
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
def get_current_user(request: Request):
    user = request.session.get('user')
    if user:
        return user
    return None

@router.post("/api/auth/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    request.session.pop('id_token', None)
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    return response

