from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "AI Cyber Platform Running v1"}
