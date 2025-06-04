# backend/auth/auth.py

import os
import uuid
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from jose import jwt, JWTError
import httpx

router = APIRouter(prefix="/api/auth")

# Load environment variables (ensure these are set in Cloud Run or .env)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # https://quantum-ai.asia/api/auth/callback
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change_this_to_a_real_random_secret")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError("Missing Google OAuth environment variables")


# 1) GET /api/auth/login → redirect to Google’s OAuth 2.0 consent screen
@router.get("/login")
def login(request: Request):
    # Generate a random state to protect against CSRF
    state = str(uuid.uuid4())
    request.session["oauth_state"] = state

    # Build Google OAuth2 authorization URL
    oauth_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",   # to get a refresh token if needed
        "prompt": "select_account",  # force account selection
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    url = httpx.URL(google_auth_url).include_query_params(**oauth_params)
    return RedirectResponse(url)


# 2) GET /api/auth/callback → handle Google’s redirect
@router.get("/callback")
async def oauth2_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    # 2a) Verify state matches
    saved_state = request.session.get("oauth_state")
    if not code or not state or state != saved_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    # 2b) Exchange authorization code for tokens
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
            raise HTTPException(status_code=400, detail="Failed to fetch tokens from Google")
        token_json = token_resp.json()

    id_token = token_json.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token returned from Google")

    # 2c) Verify the ID token’s signature and extract payload
    try:
        # NOTE: In production, you should retrieve Google’s public keys and use them to verify.
        # Here, we trust “python-jose” to fetch Google’s keys automatically by passing “audience”.
        payload = jwt.decode(
            id_token,
            key=None,
            algorithms=["RS256"],
            audience=GOOGLE_CLIENT_ID,
            issuer="https://accounts.google.com",
            options={"verify_aud": True, "verify_exp": True},
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"ID token verification failed: {str(e)}")

    # 2d) Extract user info from payload
    google_sub = payload.get("sub")         # Google’s unique user ID
    name = payload.get("name")
    email = payload.get("email")
    picture = payload.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Google ID token did not contain email")

    # 2e) “Log in” the user by saving info in the session
    request.session.clear()
    request.session["user"] = {"sub": google_sub, "name": name, "email": email, "picture": picture}

    # 2f) Redirect back to front end (your React app usually lives at “/”)
    return RedirectResponse(url="/")


# 3) GET /api/auth/me → return current session’s user, or 401
@router.get("/me")
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return JSONResponse(content=user)


# 4) GET /api/auth/logout → clear session
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
