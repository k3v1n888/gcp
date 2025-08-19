# Author: Kevin Zachary
# Copyright: Sentient Spire

import os, requests
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

INGEST_UI = os.getenv("INGEST_URL", "http://localhost:8000")

app = FastAPI(title="CXyber Console", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "console"}

@app.get("/")
def home(request: Request):
    # show mapping files
    try:
        m = requests.get(f"{INGEST_UI}/mappings", timeout=5).json()
        mappings = m.get("mappings", [])
    except Exception:
        mappings = []
    return templates.TemplateResponse("index.html", {"request": request, "mappings": mappings})

@app.get("/propose")
def propose_form(request: Request):
    return templates.TemplateResponse("propose.html", {"request": request})

@app.post("/approve")
def approve(name: str = Form(...), yaml_text: str = Form(...)):
    r = requests.post(f"{INGEST_UI}/approve_mapping", json={"name": name, "yaml_text": yaml_text}, timeout=10)
    if r.status_code == 200 and r.json().get("ok"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/?error=approve_failed", status_code=status.HTTP_303_SEE_OTHER)
