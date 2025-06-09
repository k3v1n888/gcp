import os
import uuid
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

# Google's ID-token verification
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx

# --- NEW: Import database models and session ---
from backend.models import SessionLocal, User, Tenant

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- NEW: Database dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Environment variables
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")
SESSION_SECRET_KEY   = os.getenv("SESSION_SECRET_KEY", "change_this_to_a_real_random_secret")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError(
        "Missing one of GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REDIRECT_URI"
    )

@router.get("/login")
def login(request: Request):
    state = str(uuid.uuid4())
    request.session["oauth_state"] = state
    # ... (rest of the function is unchanged)
    oauth_params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "state":         state,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    url = google_auth_url + "?" + "&".join(
        f"{key}={value}" for key, value in oauth_params.items()
    )
    return RedirectResponse(url)


@router.get("/callback")
async def oauth2_callback(
    request: Request,
    db: Session = Depends(get_db), # <-- MODIFIED: Add database dependency
    code: Optional[str] = None,
    state: Optional[str] = None
):
    # ... (existing OAuth state and token exchange logic is unchanged) ...
    saved_state = request.session.get("oauth_state")
    if not code or not state or state != saved_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_endpoint = "https://oauth2.googleapis.com/token"
    data = {
        "code":          code,
        "client_id":     GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "grant_type":    "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_endpoint, data=data)

    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")

    tokens = token_resp.json()
    id_token_str = tokens.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=400, detail="No ID token from Google")

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid ID token: {e}")

    email = idinfo.get("email")
    name = idinfo.get("name")
    picture = idinfo.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="ID token missing email")

    # --- NEW: Find or Create User in Database ---
    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        # Create a new Tenant for the new user
        new_tenant = Tenant(name=f"{name}'s Organization")
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)

        # Create the new User and make them an admin of their new tenant
        db_user = User(
            username=name,
            email=email,
            role="admin",
            tenant_id=new_tenant.id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    # --- END NEW BLOCK ---

    # --- MODIFIED: Save user info to session from the database record ---
    request.session.clear()
    request.session["user"] = {
        "id": db_user.id,
        "name": db_user.username,
        "email": db_user.email,
        "picture": picture,
        "role": db_user.role,
        "tenant_id": db_user.tenant_id
    }

    # Redirect back to React root
    return RedirectResponse(url="/")


@router.get("/me")
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return JSONResponse(content=user)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
