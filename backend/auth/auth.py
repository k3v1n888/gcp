from fastapi import APIRouter, Request, Response, HTTPException
from starlette.responses import RedirectResponse
import os

router = APIRouter()

# OAuth2 Google login stub (implement with your OAuth lib)
@router.get("/login")
def login():
    # Redirect to Google OAuth URL here
    return RedirectResponse(url="https://accounts.google.com/o/oauth2/auth?...")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@router.get("/api/auth/me")
def get_current_user(request: Request):
    user = request.session.get('user')
    if user:
        return user
    raise HTTPException(status_code=401, detail="Not authenticated")