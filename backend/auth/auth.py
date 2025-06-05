# backend/auth/auth.py
# ──────────────────────────────────────────────────────────────────────────────

import os
import uuid
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Environment variables (must be set in Cloud Run or in your local .env)
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  # not actually used by id_token.verify_oauth2_token
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")   # e.g. "https://quantum-ai.asia/api/auth/callback"
SESSION_SECRET_KEY   = os.getenv("SESSION_SECRET_KEY", "change_this_to_a_real_random_secret")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError("Missing one of GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REDIRECT_URI")


@router.get("/login")
def login(request: Request):
    """
    1) Redirect user to Google’s OAuth 2.0 consent screen.
    """
    state = str(uuid.uuid4())
    request.session["oauth_state"] = state

    oauth_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(
        f"{key}={value}" for key, value in oauth_params.items()
    )
    return RedirectResponse(url)


@router.get("/callback")
async def oauth2_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    """
    2) Google calls back here with ?code=…&state=….
       We exchange for tokens, verify ID token, store user in session, then redirect to “/”.
    """
    saved_state = request.session.get("oauth_state")
    if not code or not state or state != saved_state:
        raise HTTPException(status_code=400, detail="Invalid or missing OAuth state/token")

    token_endpoint = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_endpoint, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    tokens = token_resp.json()
    id_token_str = tokens.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=400, detail="No ID token in response from Google")

    # Use google-auth to verify the ID token signature & audience:
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid ID token: {e}")

    # Extract user info from the verified token
    google_sub = idinfo.get("sub")
    name       = idinfo.get("name")
    email      = idinfo.get("email")
    picture    = idinfo.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="ID token did not contain email")

    # Log in the user by saving info in session
    request.session.clear()
    request.session["user"] = {
        "sub": google_sub,
        "name": name,
        "email": email,
        "picture": picture,
    }

    # Redirect back to React SPA root
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
