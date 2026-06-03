"""Minimal test app for Railway debugging."""
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return "SentinelX MVP - alive"

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
