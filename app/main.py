"""FastAPI application entry point."""

from app.models import SystemReport
from fastapi import FastAPI
from app.collector import get_system_info, get_top_processes

app=FastAPI(
    title="System Reporter API",
    description="API de monitoring du systeme et des processus",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "System Reporter API",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health():
    """Endpoint de santé de l'API."""
    return {"status": "ok"}

@app.get("/metrics",response_model=SystemReport)
def metrics():
    """Retourne les metriques du systeme et les informations sur les processus."""
    data=get_system_info()
    data["top_processes"]=get_top_processes(5)
    return data
